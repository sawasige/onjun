require './config.pl';
require './jcode.pl';
require './phone.pl';

use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
use DBI;
use EscapeSJIS;
use Image::Magick;
use Fcntl ':flock';

my $cgi = new CGI;
# �ݒ�Ǎ�
my %config = &config;

my $phone = &phone_info();

##################
# CGI �I�u�W�F�N�g�擾
sub getCGI() {
	return $cgi;
}

##################
# �ݒ�擾
sub getConfig() {
	return %config;
}

################
# URL �G���R�[�h
sub urlEncode {
	my $str = shift;
	$str =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;    #�����ŃG���R�[�h
	return($str);
}

####################
# �Z�b�V�����ǂݍ���
sub readSession($) {
	my $login = shift;

	#1.cookie ���� sid ��T��
	#2.cookie ������Ȃ�������p�����[�^��T���D
	#3.�ǂ�����擾�ł��Ȃ�������Z�b�V�����؂�B
	my $sid;
	if (&isMobile()) {
		$sid = $cgi->param($config{'sessionname'}) || undef;
	} else {
		$sid = $cgi->cookie($config{'sessionname'}) || $cgi->param($config{'sessionname'}) || undef;
	}
	my $session = CGI::Session->new(undef, $sid, {Directory=>$config{'sessiondir'}});
	
	if ($login && $session->param('userid')) {
		# ���탍�O�C��
	} elsif ($login) {
		# URL ��ۑ����ă��O�C����ʂ֑J��
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
		$session->param('msg', '���O�C�����Ă��������B');
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
		# ���O�C���O�ŃZ�b�V�����擾
	}
	return($session);
}

######################
# �e���v���[�g�ǂݍ���
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
# ���̕�����擾
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
		return $age.'��'.$year.'�N����';
	} else {
		return $age.'��'.$class.'�N��';
	}
}

##################
# �g�є��ʕϐ��擾
sub getPhone() {
	return $phone;
}


############
# �g�т��ۂ�
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
# �g�� UID �擾
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
# DB �ڑ�
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
# DB �ؒf
sub disconnectDB($) {
	my $dbh = shift;
	$dbh->disconnect()
		or die("$DBI::err:$DBI::errstr");
}

################
# DB �N�G�����s
sub doDB($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	my $rv = $dbh->do($sql, undef, @bind)
		or die("$DBI::err:$DBI::errstr");
	return $rv;
}

###############################
# DB �N�G�������s���Ēl���擾
sub selectFetch($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# �Ǘ����[�U�[���쐬
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
# DB �N�G�������s���Ēl�� 1 ��������z��Ŏ擾
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
# DB �N�G�������s���Ēl�����t�@�����X�̔z��Ŏ擾
sub selectFetchArrayRef($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# �Ǘ����[�U�[���쐬
	my $sth = $dbh->prepare($sql);
	$sth->execute(@bind);
	my $rows = $sth->fetchall_arrayref();
	return @$rows;
}

##############
# �o�͕ϊ�
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
# ���̓`�F�b�N
sub checkString($) {
	my $label = shift;
	my $val = shift;
	my $len = shift;
	my $notnull = shift;
	
	if (length ($val) > $len) {
		return $label.'�̕�������'.$len.'�����ȓ��œ��͂��Ă��������B';
	}
	if ($notnull && $val eq '') {
		return $label.'�����͂���Ă��܂���B';
	}
#	if ($val && $val !~ /[ -~�-�\�@-\�K]/) {
#		return $label.'�ɕs���ȕ������g���Ă��܂��B';
#	}

	return undef;
}

##############
# ���t���̓`�F�b�N
sub checkDateString($) {
	my $label = shift;
	my $val = shift;
	my $notnull = shift;
	
	if ($notnull && $val eq '') {
		return $label.'�����͂���Ă��܂���B';
	}
	if (!$notnull && $val eq '') {
		return undef;
	}
	if ($val =~ /^([0-9][0-9][0-9][0-9])([0-9][0-9])([0-9][0-9])$/) {
		my ($y, $m, $d);
		($y, $m, $d) = ($1, $2, $3);
		if ($m < 1 or $m > 12) {
			return $label.'�̌��̎w�肪����������܂���B';
		} else {
			my @mday = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
			if ($m == 2 && ((($y % 4 == 0) && ($y % 100 != 0)) || ($y % 400 == 0))) {
				$mday[1]++;
			}
			if ($d < 1 or $d > $mday[$m-1]) {
				return $label.'�̓��̎w�肪����������܂���B';
			}
		}
	} else {
		return $label.'��YYYYMMDD�̌`�œ��͂��Ă��������B';
	}

	return undef;
}

######################
# �A�b�v���[�h�t�@�C���`�F�b�N
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
# �Y�t�t�@�C���`�F�b�N
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
# �t�@�C���T�C�Y����
sub ajustFile($) {
	my $lname = shift;
	my $sname = shift;
	my @return = ();
	my $img = Image::Magick->new();

	if ($img->Read("$config{'sessiondir'}/$lname")) {
		# �摜�ȊO
		unlink("$config{'sessiondir'}/$lname");
	} else {
		# �ʏ�T�C�Y�摜�t�@�C����
		push(@return, $lname);
		# �摜
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
		# �T���l�C���쐬
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
			# �T���l�C���T�C�Y�摜�t�@�C����
			push(@return, $sname);
		}
	}
	return @return;
}

#################
# �A�b�v���[�h�t�@�C�����J
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
# �A�b�v���[�h�t�@�C���p�X�擾
sub getPublishFile($) {
	my $file = shift;
	my $path = $config{'uploaddir'}.'/'.$file;
	foreach (glob("$path*")) {
		return $_;
	}
	return 0;
}

###################################
# �A�b�v���[�h�t�@�C���폜�i�ق�Ƃ��ɍ폜�j
sub deleteFile($) {
	my $file = shift;
	my $path = $config{'uploaddir'}.'/'.$file;
	foreach (glob("$path*")) {
		unlink($_);
	}
}

###################################
# �A�b�v���[�h�t�@�C���폜�i�폜�̈�Ɉړ��j
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
# �����_�������񐶐�
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
# �I�����C�����
sub checkOnline($) {
	my ($dbh, $userid, $title) = @_;
	my $msg = '';
	# 5 ���o�߂������̂̓I�t���C��
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
# ���O�o��
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
		
		# �t�@�C����������
		open(OUT,">> $filename");
		flock(OUT, LOCK_EX);
		print OUT $line;
		close(OUT);
	}

	# 30 ���� 1 �̊m���ŃK�x�[�W�R���N�V����
	if (int(rand(30)) == 1) {
		my @files = glob($config{'logdir'}.'/*');
		foreach my $file(@files) {
			my $lastmodified = (stat $file)[9];
			# 30���Ԍo�߂����t�@�C���͍폜
			if ($lastmodified < time() - 60 * 60 * 24 * 30) {
				unlink($file);
			}
		}
	}
}


################
# ���񂽂܎擾
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
# ���񂽂܂̏�Ԏ擾
sub getOntamaStatus($) {
	my ($dbh, $userid, %ontama) = @_;
	my @status = ();

	push(@status, $ontama{'days'}.'���ڂł��B');

	# DB �Ɏc���Ă���
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
		push(@status, '�S�n����'.$ontama{'food'}.'���炢�܂������A�܂��H�ׂĂ��܂���B');
	}
	
	if ($ontama{'hungry'} >= 90) {
		push(@status, '���Ȃ����͂����ꂻ���ł��B');
	} elsif ($ontama{'hungry'} >= 50) {
		push(@status, '���Ȃ������ς��ł��B');
	} elsif ($ontama{'hungry'} <= 0) {
		push(@status, '���ʂقǂ��Ȃ��������Ă܂��B');
	} elsif ($ontama{'hungry'} < 10) {
		push(@status, '���Ȃ肨�Ȃ��������Ă܂��B');
	} elsif ($ontama{'hungry'} < 20) {
		push(@status, '���Ȃ��������Ă܂��B');
	} elsif ($ontama{'hungry'} < 30) {
		push(@status, '������Ƃ��Ȃ��������Ă܂��B');
	}

	if ($ontama{'happy'} >= 90) {
		push(@status, '��������悤�ɂ�������ł��B');
	} elsif ($ontama{'happy'} >= 50) {
		push(@status, '��������ł��B');
	} elsif ($ontama{'happy'} <= 0) {
		push(@status, '���ʂقǓ{���Ă܂��B');
	} elsif ($ontama{'happy'} < 10) {
		push(@status, '���Ȃ�{���Ă܂��B');
	} elsif ($ontama{'happy'} < 20) {
		push(@status, '�{���Ă܂��B');
	} elsif ($ontama{'happy'} < 30) {
		push(@status, '�@�������ł��B');
	}

	if ($ontama{'health'} >= 90) {
		push(@status, '���N�ł��B');
	} elsif ($ontama{'health'} >= 70) {
		push(@status, '�قǂ悭���N�ł��B');
	} elsif ($ontama{'health'} <= 0) {
		@status = ();
		push(@status, $ontama{'days'}.'���ڂɎ��񂶂Ⴂ�܂����B');
	} elsif ($ontama{'health'} < 20) {
		push(@status, '�z���g�Ɏ��ɂ����ł��B');
	} elsif ($ontama{'health'} < 40) {
		push(@status, '���q�����ł��B');
	}
	
	if (@status <= 1 && $ontama{'health'} > 0) {
		push(@status, '�������ʂł��B');
	}
	return @status;
}


1;
