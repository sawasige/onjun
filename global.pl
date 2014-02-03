require './config.pl';
require './jcode.pl';
require './phone.pl';

use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;
use CGI::Session;
use HTML::Template;
use DBI;
use EscapeSJIS;
use Image::Magick;
use Fcntl ':flock';

my $cgi = new CGI;
# 設定読込
my %config = &config;

my $phone = &phone_info();

##################
# CGI オブジェクト取得
sub getCGI() {
	return $cgi;
}

##################
# 設定取得
sub getConfig() {
	return %config;
}

################
# URL エンコード
sub urlEncode {
	my $str = shift;
	$str =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;    #ここでエンコード
	return($str);
}

####################
# セッション読み込み
sub readSession($) {
	my $login = shift;

	#1.cookie から sid を探す
	#2.cookie から取れなかったらパラメータを探す．
	#3.どちらも取得できなかったらセッション切れ。
	my $sid;
	if (&isMobile()) {
		$sid = $cgi->param($config{'sessionname'}) || undef;
	} else {
		$sid = $cgi->cookie($config{'sessionname'}) || $cgi->param($config{'sessionname'}) || undef;
	}
	my $session = CGI::Session->new(undef, $sid, {Directory=>$config{'sessiondir'}});
	
	if ($login && $session->param('userid')) {
		# 正常ログイン
	} elsif ($login) {
		# URL を保存してログイン画面へ遷移
		my $saveurl = $cgi->url();
		my @params = $cgi->param();
		my $i = 0;
		foreach my $param(@params){
			if ($param eq $config{'sessionname'}) {
				next;
			}
			if ($i) {
				$saveurl .= "&$param=".$cgi->param($param);
			} else {
				$saveurl .= "?$param=".$cgi->param($param);
			}
			$i++;
		}
		$session->param('openurl', $saveurl);
		$session->param('msg', 'ログインしてください。');
		my $url = 'login.cgi';
		if (&isMobile()) {
			print $cgi->redirect($url.'?'.$config{'sessionname'}.'='.$session->id());
		} else {
			print $cgi->redirect(
				-uri=>$url,
				-cookie=>$cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id()));
		}
		$session = undef;
	} else {
		# ログイン外でセッション取得
	}
	return($session);
}

######################
# テンプレート読み込み
sub readTemplate() {
	my $cginame = $cgi->url(-relative=>1);
	if (!$cginame) {
		$cginame = 'index.cgi';
	}

	my $tmpl;
	if ($phone->{type} eq "docomo") {
		$tmpl = HTML::Template->new(filename => "$config{'tmpldir_i'}/$cginame.tmpl");
	} elsif ($phone->{type} eq "ezweb") {
		$tmpl = HTML::Template->new(filename => "$config{'tmpldir_ez'}/$cginame.tmpl");
	} elsif ($phone->{type} eq "jphone") {
		$tmpl = HTML::Template->new(filename => "$config{'tmpldir_v'}/$cginame.tmpl");
	} else {
		$tmpl = HTML::Template->new(filename => "$config{'tmpldir'}/$cginame.tmpl");
	}
}


##################
# 期の文字列取得
sub getAgeString($) {
	my $age = shift;
	my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
	$now_year = $now_year + 1900;
	$now_month++;
	my $year = $age + 1976;
	my $class = $now_year - $year + 3;
	if ($now_month >= 4) {
		$class++;
	}
	if ($class > 3) {
		return $age.'期'.$year.'年卒業';
	} else {
		return $age.'期'.$class.'年生';
	}
}

##################
# 携帯判別変数取得
sub getPhone() {
	return $phone;
}


############
# 携帯か否か
sub isMobile() {
	if ($phone->{type} eq "docomo") {
		return 1;
	} elsif ($phone->{type} eq "ezweb") {
		return 1;
	} elsif ($phone->{type} eq "jphone") {
		return 1;
	} else {
		return 0;
	}
}

##################
# 携帯 UID 取得
sub getPhoneID() {
	my $key = undef;
	if ($phone->{uid}) {
		$key = $phone->{uid};
	} elsif ($phone->{type} eq "docomo") {
		my ($first, $second) = (split(/\//,$ENV{'HTTP_USER_AGENT'}))[0,1];
		if($first eq 'DoCoMo') {
			if ($second eq '1.0') {
				if ($ENV{'HTTP_USER_AGENT'} =~ /(ser[a-zA-Z0-9]+)/) {
					$key = $1;
				}
			} elsif ($second =~ /^2.0 /){
				if ($ENV{'HTTP_USER_AGENT'} =~ /(icc[a-zA-Z0-9]+)/) {
					$key = $1;
				}
			}
		}
	} elsif ($phone->{type} eq "jphone") {
		my $sn = (split(/\//,$ENV{'HTTP_USER_AGENT'}))[3];
		if ($sn =~ /^(SN[a-zA-Z0-9]+)/) {
			$key = $1;
		}
	}
	return $key;
}



##########
# DB 接続
sub connectDB($) {
	my $raiseError = shift;
	if ($raiseError == 1) {
		$raiseError = 1;
	} else {
		$raiseError = 0;
	}
	my $dbh = DBI->connect($config{'db_source'}, $config{'db_user'}, $config{'db_pass'})
		or die("$DBI::err:$DBI::errstr");
	$dbh->{RaiseError} = $raiseError;
	return $dbh
}

##########
# DB 切断
sub disconnectDB($) {
	my $dbh = shift;
	$dbh->disconnect()
		or die("$DBI::err:$DBI::errstr");
}

################
# DB クエリ実行
sub doDB($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	my $rv = $dbh->do($sql, undef, @bind)
		or die("$DBI::err:$DBI::errstr");
	return $rv;
}

###############################
# DB クエリを実行して値を取得
sub selectFetch($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# 管理ユーザーを作成
	my $sth = $dbh->prepare($sql)
		or die("$DBI::err:$DBI::errstr");
	$sth->execute(@bind)
		or die("$DBI::err:$DBI::errstr");
	my @row = $sth->fetchrow_array();
	if (@row) {
		return $row[0];
	} else {
		return undef;
	}
}

###############################
# DB クエリを実行して値を 1 件だけを配列で取得
sub selectFetchArray($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	my $sth = $dbh->prepare($sql)
		or die("$DBI::err:$DBI::errstr".'0');
	$sth->execute(@bind)
		or die("$DBI::err:$DBI::errstr".'1');
	my @row = $sth->fetchrow_array();
	return @row;
}

#################################################
# DB クエリを実行して値をリファレンスの配列で取得
sub selectFetchArrayRef($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# 管理ユーザーを作成
	my $sth = $dbh->prepare($sql);
	$sth->execute(@bind);
	my $rows = $sth->fetchall_arrayref();
	return @$rows;
}

##############
# 出力変換
sub convertOutput($) {
	my $val = shift;
	my $escLf = shift;
	$val =~ s/\r\n/\n/g;
	#$val =~ s/^\n+//;
	#$val =~ s/\n+$//;
	$val =~ s/</&lt;/g;
	$val =~ s/>/&gt;/g;
	if ($escLf) {
		$val =~ s/\n/\<br\>/g;
	}
	return $val;
}

##############
# 入力チェック
sub checkString($) {
	my $label = shift;
	my $val = shift;
	my $len = shift;
	my $notnull = shift;
	
	if (length ($val) > $len) {
		return $label.'の文字数は'.$len.'文字以内で入力してください。';
	}
	if ($notnull && $val eq '') {
		return $label.'が入力されていません。';
	}
#	if ($val && $val !~ /[ -~｡-ﾟ\　-\黑]/) {
#		return $label.'に不正な文字が使われています。';
#	}

	return undef;
}

##############
# 日付入力チェック
sub checkDateString($) {
	my $label = shift;
	my $val = shift;
	my $notnull = shift;
	
	if ($notnull && $val eq '') {
		return $label.'が入力されていません。';
	}
	if (!$notnull && $val eq '') {
		return undef;
	}
	if ($val =~ /^([0-9][0-9][0-9][0-9])([0-9][0-9])([0-9][0-9])$/) {
		my ($y, $m, $d);
		($y, $m, $d) = ($1, $2, $3);
		if ($m < 1 or $m > 12) {
			return $label.'の月の指定が正しくありません。';
		} else {
			my @mday = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
			if ($m == 2 && ((($y % 4 == 0) && ($y % 100 != 0)) || ($y % 400 == 0))) {
				$mday[1]++;
			}
			if ($d < 1 or $d > $mday[$m-1]) {
				return $label.'の日の指定が正しくありません。';
			}
		}
	} else {
		return $label.'はYYYYMMDDの形で入力してください。';
	}

	return undef;
}

######################
# アップロードファイルチェック
sub uploadFile($) {
	my $file = shift;
	my $no = shift;
	my $sid = shift;
	my $ext = '';
	if ($file =~ m|(\.[^./\\]+)$|) {
		$ext = lc($1);
	}
	if ($ext ne '.jpg' && $ext ne '.jpeg' && $ext ne '.gif' && $ext ne '.png') {
		return 0;
	}
	my $lname = 'file'.$no.'_'.$sid.$ext;
	my $sname = 'file'.$no.'_s_'.$sid.$ext;
	open(OUT, "> $config{'sessiondir'}/$lname");
	while (<$file>) {
		print OUT $_;
	}
	close OUT;

	my @return = &ajustFile($lname, $sname);
	return @return;
}

######################
# 添付ファイルチェック
sub attachFile($) {
	my $file = shift;
	my $no = shift;
	my $sid = shift;
	my $ext = '';
	if ($file =~ m|(\.[^./\\]+)$|) {
		$ext = lc($1);
	}
	if ($ext ne '.jpg' && $ext ne '.jpeg' && $ext ne '.gif' && $ext ne '.png') {
		return 0;
	}
	my $lname = 'file'.$no.'_'.$sid.$ext;
	my $sname = 'file'.$no.'_s_'.$sid.$ext;
	rename($file, "$config{'sessiondir'}/$lname");

	my @return = &ajustFile($lname, $sname);
	return @return;
}

########################
# ファイルサイズ調整
sub ajustFile($) {
	my $lname = shift;
	my $sname = shift;
	my @return = ();
	my $img = Image::Magick->new();

	if ($img->Read("$config{'sessiondir'}/$lname")) {
		# 画像以外
		unlink("$config{'sessiondir'}/$lname");
	} else {
		# 通常サイズ画像ファイル名
		push(@return, $lname);
		# 画像
		my ($w, $h) = $img->Get('width', 'height');
		my $resize = 0;
		if ($w > $config{'image_maxsize'}) {
			$h = int($config{'image_maxsize'} * $h / $w);
			$w = $config{'image_maxsize'};
			$resize = 1;
		}
		if ($h > $config{'image_maxsize'}) {
			$w = int($config{'image_maxsize'} * $w / $h);
			$h = $config{'image_maxsize'};
			$resize = 1;
		}
		if ($resize) {
			$img->Resize(width => $w, height => $h);
			$img->Write("$config{'sessiondir'}/$lname");
		}
		# サムネイル作成
		$resize = 0;
		if ($w > $config{'image_s_maxsize'}) {
			$h = int($config{'image_s_maxsize'} * $h / $w);
			$w = $config{'image_s_maxsize'};
			$resize = 1;
		}
		if ($h > $config{'image_s_maxsize'}) {
			$w = int($config{'image_s_maxsize'} * $w / $h);
			$h = $config{'image_s_maxsize'};
			$resize = 1;
		}
		if ($resize) {
			$img->Resize(width => $w, height => $h);
			$img->Write("$config{'sessiondir'}/$sname");
			# サムネイルサイズ画像ファイル名
			push(@return, $sname);
		}
	}
	return @return;
}

#################
# アップロードファイル公開
sub publishFile($) {
	my $src = shift;
	if (!$src) {
		return 0;
	}
	my $dst = shift;
	my $srcpath = "$config{'sessiondir'}/$src";
	if (-e $srcpath) {
		my $ext = '';
		if ($src =~ m|(\.[^./\\]+)$|) {
			$ext = lc($1);
		}
		rename($srcpath, "$config{'uploaddir'}/$dst$ext");
		return 1;
	}
	return 0;
}

#######################
# アップロードファイルパス取得
sub getPublishFile($) {
	my $file = shift;
	my $path = $config{'uploaddir'}.'/'.$file;
	foreach (glob("$path*")) {
		return $_;
	}
	return 0;
}

###################################
# アップロードファイル削除（ほんとうに削除）
sub deleteFile($) {
	my $file = shift;
	my $path = $config{'uploaddir'}.'/'.$file;
	foreach (glob("$path*")) {
		unlink($_);
	}
}

###################################
# アップロードファイル削除（削除領域に移動）
sub hideFile($) {
	my $file = shift;
	my $path = $config{'uploaddir'}.'/'.$file;
	foreach my $src(glob("$path*")) {
		if ($src =~ /(.+)\/([^\/]+)$/) {
			my $dst = $config{'deleteddir'}.'/'.$2;
			rename($src, $dst);
		}
	}
}

#####################
# ランダム文字列生成
sub getRandomString($) {  #($len, $str)
  my ($len, $str) = @_;
  my @str = $str ? split //, $str : ('A'..'Z','a'..'z','0'..'9');

  undef $str;
  $len = 8 if (!$len);
  for (1 .. $len) {
    $str .= $str[int rand($#str+1)];
  }
  return $str;
}


#################
# オンライン状態
sub checkOnline($) {
	my ($dbh, $userid, $title) = @_;
	my $msg = '';
	# 5 分経過したものはオフライン
	my $sql = 
		'UPDATE onlineusers SET deleteflag=? WHERE deleteflag=? AND DATE_ADD(registtime, INTERVAL 5 MINUTE) < now()';
	&doDB($dbh, $sql, ('1', '0'));

	if ($userid) {
		my $username = &selectFetch($dbh, 'SELECT name FROM users WHERE userid=?', $userid);
		&writeLog(2, $username.':'.$title);
		
		if (&selectFetch($dbh, 'SELECT count(*) FROM onlineusers WHERE userid=?', $userid)) {
			my $sql = 
				'UPDATE onlineusers SET'.
				' deleteflag=?,'.
				' registtime=now(),'.
				' title=?'.
				' WHERE'.
				' userid=?';
			my @bind = ('0', $title, $userid);
			&doDB($dbh, $sql, @bind);
		} else {
			my $sql = 
				'INSERT onlineusers ('.
				' userid,'.
				' deleteflag,'.
				' registtime,'.
				' title'.
				') VALUES (?, ?, now(), ?)';
			my @bind = ($userid, '0', $title);
			&doDB($dbh, $sql, @bind);
		}
	} else {
		&writeLog(2, 'Guest:'.$title);
	}
	
	return $msg;
}

################
# ログ出力
sub writeLog($) {
	my ($level, $text) = @_;
	
	if ($level >= $config{'loglevel'}) {	
		my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
		$now_year = $now_year + 1900;
		$now_month++;
		
		
		my $time = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $now_year, $now_month, $now_mday, $now_hour, $now_min, $now_sec);
		my $filename = $config{'logdir'}.'/'.sprintf("%04d%02d%02d", $now_year, $now_month, $now_mday).'.log';
		my $useragent = $ENV{'HTTP_USER_AGENT'};
		my $remoteaddr = $ENV{'REMOTE_ADDR'};
		my $line = "$time\t$level\t$useragent\t$remoteaddr\t$text\n";
		
		# ファイル書き込み
		open(OUT,">> $filename");
		flock(OUT, LOCK_EX);
		print OUT $line;
		close(OUT);
	}

	# 30 分の 1 の確率でガベージコレクション
	if (int(rand(30)) == 1) {
		my @files = glob($config{'logdir'}.'/*');
		foreach my $file(@files) {
			my $lastmodified = (stat $file)[9];
			# 30日間経過したファイルは削除
			if ($lastmodified < time() - 60 * 60 * 24 * 30) {
				unlink($file);
			}
		}
	}
}


################
# おんたま取得
sub getOntama($) {
	my ($dbh, $userid) = @_;
	my $sql = 
		'SELECT'.
		' a.maxgrow,'.
		' a.healthdiff,'.
		' a.hungrydiff,'.
		' a.happydiff,'.
		' b.name,'.
		' b.image,'.
		' b.days,'.
		' b.level,'.
		' b.grow,'.
		' b.health,'.
		' b.hungry,'.
		' b.happy,'.
		' b.food,'.
		' c.name'.
		' FROM'.
		' ontama a,'.
		' ontamausers b,'.
		' users c'.
		' WHERE'.
		' a.ontamaid = b.ontamaid AND'.
		' b.userid = c.userid AND'.
		' b.userid = ? AND'.
		' c.deleteflag = ?';

	my ($maxgrow, $healthdiff, $hungrydiff, $happydiff, $name, $image, $days, $level, $grow, $health, $hungry, $happy, $food, $ownername) = &selectFetchArray($dbh, $sql, ($userid, '0'));
	my %ontama;
	$ontama{'maxgrow'} = $maxgrow;
	$ontama{'healthdiff'} = $healthdiff;
	$ontama{'hungrydiff'} = $hungrydiff;
	$ontama{'happydiff'} = $happydiff;
	$ontama{'name'} = $name;
	$ontama{'image'} = $image;
	$ontama{'days'} = $days;
	$ontama{'level'} = $level;
	$ontama{'grow'} = $grow;
	$ontama{'health'} = $health;
	$ontama{'hungry'} = $hungry;
	$ontama{'happy'} = $happy;
	$ontama{'food'} = $food;
	$ontama{'ownername'} = $ownername;
	return %ontama;
}

#####################
# おんたまの状態取得
sub getOntamaStatus($) {
	my ($dbh, $userid, %ontama) = @_;
	my @status = ();

	push(@status, $ontama{'days'}.'日目です。');

	# DB に残ってる状態
	my @ontamastatus = &selectFetchArrayRef($dbh, 'SELECT body FROM ontamastatus WHERE userid=?', $userid);
	foreach my $row(@ontamastatus) {
		my ($body) = @$row;
		push(@status, $body);
	}

	if ($ontama{'food'}) {
		if ($ontama{'food'} > 10) {
			$ontama{'food'} = 10;
		}
		if ($ontama{'food'} < 0) {
			$ontama{'food'} = 0;
		}
		push(@status, 'ゴハンを'.$ontama{'food'}.'個もらいましたが、まだ食べていません。');
	}
	
	if ($ontama{'hungry'} >= 90) {
		push(@status, 'おなかがはちきれそうです。');
	} elsif ($ontama{'hungry'} >= 50) {
		push(@status, 'おなかいっぱいです。');
	} elsif ($ontama{'hungry'} <= 0) {
		push(@status, '死ぬほどおなかがすいてます。');
	} elsif ($ontama{'hungry'} < 10) {
		push(@status, 'かなりおなかがすいてます。');
	} elsif ($ontama{'hungry'} < 20) {
		push(@status, 'おなかがすいてます。');
	} elsif ($ontama{'hungry'} < 30) {
		push(@status, 'ちょっとおなかがすいてます。');
	}

	if ($ontama{'happy'} >= 90) {
		push(@status, 'くるったようにごきげんです。');
	} elsif ($ontama{'happy'} >= 50) {
		push(@status, 'ごきげんです。');
	} elsif ($ontama{'happy'} <= 0) {
		push(@status, '死ぬほど怒ってます。');
	} elsif ($ontama{'happy'} < 10) {
		push(@status, 'かなり怒ってます。');
	} elsif ($ontama{'happy'} < 20) {
		push(@status, '怒ってます。');
	} elsif ($ontama{'happy'} < 30) {
		push(@status, '機嫌悪いです。');
	}

	if ($ontama{'health'} >= 90) {
		push(@status, '健康です。');
	} elsif ($ontama{'health'} >= 70) {
		push(@status, 'ほどよく健康です。');
	} elsif ($ontama{'health'} <= 0) {
		@status = ();
		push(@status, $ontama{'days'}.'日目に死んじゃいました。');
	} elsif ($ontama{'health'} < 20) {
		push(@status, 'ホントに死にそうです。');
	} elsif ($ontama{'health'} < 40) {
		push(@status, '調子悪いです。');
	}
	
	if (@status <= 1 && $ontama{'health'} > 0) {
		push(@status, 'ごく普通です。');
	}
	return @status;
}


1;
