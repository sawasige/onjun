#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './jcode.pl';

my $cgi;
my %config;
my $msg;
my $session;
my $sid;

my $dbh;
my @ages = ();
my $usercount = 0;
my @users = ();

#プログラム開始
&main;

##########
# メイン
sub main {
	$cgi = new CGI;
	$msg = '';

	# 設定読み込み
	%config = &config;

	# セッション読み込み
	$session = &readSession(1);
	if (defined $session) {
		$sid = $session->id;

		# DB オープン
		$dbh = &connectDB(1);

		# 検索
		if ($cgi->param('submit') || !$cgi->param('search')) {
			&searchUser();
		}

		# 選択項目取得
		&getValues();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'メンバー一覧');

		# 画面表示
		&disp;

		# DB クローズ
		&disconnectDB($dbh);
	}
}

###########
# 画面表示
sub disp {
	# テンプレート読み込み
	my $tmpl = &readTemplate($cgi);

	# 共通テンプレート変数セット
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	my $job = '';
	my $part = '';
	my $age = '';
	if ($cgi->param('submit')) {
		$job = $cgi->param('job');
		$part = $cgi->param('part');
		$age = $cgi->param('age');
#	} else {
#		$age = &getUserAge();
	}
	
	# メッセージ
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();

	# 検索の URL
	if ($tmpl->query(name => 'URL_MEMBERSEARCH') eq 'VAR') {
		my $url = 'memberlist.cgi?search=1';
		if (&isMobile) {
			$url .= '&'.$config{'sessionname'}.'='.$session->id;
		}
		$tmpl->param(URL_MEMBERSEARCH => &convertOutput($url));
	}
	
	# 職業
	if ($tmpl->query(name => 'JOB') eq 'VAR') {
		$tmpl->param(JOB => &convertOutput($job));
	}
	# パート（楽器）
	if ($tmpl->query(name => 'PART') eq 'VAR') {
		$tmpl->param(PART => &convertOutput($part));
	}

	# 期
	if ($tmpl->query(name => 'AGE') eq 'LOOP') {
		my %age;
		$age{AGEVALUE} = '';
		$age{AGESELECTED} = $age eq '' && 'selected';
		$age{AGELABEL} = '未選択';
		my @agedata = ();
		push(@agedata, \%age);
		foreach my $row(@ages) {
			my ($ageid, $name) = @$row;
			my %age;
			$age{AGEVALUE} = $ageid;
			$age{AGESELECTED} = $age eq $ageid && 'selected';
			$age{AGELABEL} = $name;
			push(@agedata, \%age);
		}
		$tmpl->param(AGE => \@agedata);
	}

	# メンバー一覧
	if (@users && $tmpl->query(name => 'MEMBERS') eq 'LOOP') {
		my @userdata = ();
		foreach my $row(@users) {
			my ($userid, $name, $job, $part, $age, $note, $registtime) = @$row;
			my %user;
			# プロフィール URL
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				# セッション
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$user{'MEMBERURL'} = &convertOutput($url);
			}
			# ユーザー名
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERNAME']) eq 'VAR') {
				$user{'MEMBERNAME'} = &convertOutput($name);
			}
			# 職業
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERJOB']) eq 'VAR') {
				$user{'MEMBERJOB'} = &convertOutput($job);
			}
			# 楽器
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERPART']) eq 'VAR') {
				$user{'MEMBERPART'} = &convertOutput($part);
			}
			# 期
			if ($age && $tmpl->query(name => ['MEMBERS', 'MEMBERAGE']) eq 'VAR') {
				$user{'MEMBERAGE'} = &convertOutput(&getAgeString($age));
			}
			# 時間
			if ($tmpl->query(name => ['MEMBERS', 'TIME']) eq 'VAR') {
				$user{'TIME'} = &convertOutput($registtime);
			}
			# 日付
			if ($tmpl->query(name => ['MEMBERS', 'DATE']) eq 'VAR') {
				if ($registtime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$user{'DATE'} = &convertOutput($2.'月'.$3.'日');
				}
			}
			push(@userdata, \%user);
		}
		$tmpl->param(MEMBERS => \@userdata);
	}

	# 前ページ
	if ($cgi->param('start') > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $url = $cgi->url(-relative=>1).'?';
		$url .= 'submit=1';
		# 開始行
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $prevstart = $cgi->param('start') - $pagesize;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		$url .= '&start='.$prevstart;
		$url .= '&size='.$pagesize;
		$url .= &getCondUrl();
		$tmpl->param(PREVPAGEURL => &convertOutput($url));
	}

	# 前ページ番号
	if ($cgi->param('start') > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $start = $cgi->param('start') + 0;
		my $no = int($start / $pagesize) + 1;
		my $startno = 1;
		if ($no > 10) {
			$startno = $no - 10
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1).'?';
			$url .= 'submit=1';
			# 開始行
			$url .= '&start='.($i-1) * $pagesize;
			$url .= '&size='.$pagesize;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGEURL']) eq 'VAR') {
				$page{BACKPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGELABEL']) eq 'VAR') {
				$page{BACKPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
		}
		$tmpl->param(BACKPAGELOOP => \@pagedata);
	}

	# 次ページ
	if (($cgi->param('start') + @users) < $usercount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $url = $cgi->url(-relative=>1).'?';
		$url .= 'submit=1';
		# 開始行
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $nextstart = $cgi->param('start') + $pagesize;
		$url .= '&start='.$nextstart;
		$url .= '&size='.$pagesize;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# 次ページ番号
	if (($cgi->param('start') + @users) < $usercount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $start = $cgi->param('start') + 0;
		my $no = int($start / $pagesize) + 1;
		my $maxno = int($usercount / $pagesize);
		if ($usercount % $pagesize) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1).'?';
			$url .= 'submit=1';
			# 開始行
			$url .= '&start='.($i-1) * $pagesize;
			$url .= '&size='.$pagesize;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 10 ページ以上は移動できない
			if (@pagedata >= 10) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# 現在ページ
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		# ページ処理する場合だけ表示
		if ($pagesize < $usercount) {
			my $start = $cgi->param('start') + 0;
			my $no = int($start / $pagesize) + 1;
			$tmpl->param(NOWPAGENOLABEL => $no);
		}
	}


	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###########################
# 検索条件を URL エンコード
sub getCondUrl {
	my $url = '';
	# セッション
	if (&isMobile) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id;
	}
	# 職業
	if ($cgi->param('job')) {
		$url .= '&job='.&urlEncode($cgi->param('job'));
	}
	# パート（楽器）
	if ($cgi->param('part')) {
		$url .= '&part='.&urlEncode($cgi->param('part'));
	}
	# 期
	if ($cgi->param('age')) {
		$url .= '&age='.&urlEncode($cgi->param('age'));
	}
	return $url;
}

################
# 選択項目取得
sub getValues() {
	# 期
	@ages = ();
	my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
	$now_year = $now_year + 1900;
	$now_month++;
	for (my $i = $now_year - 1976 + 3; $i >= 1; $i--) {
		my $year = $i + 1976;
		my $class = $now_year - $year + 3;
		if ($now_month >= 4) {
			$class++;
		}
		my $age;
		if ($class > 3) {
			$age = [$i, $i.'期'.$year.'年卒業'];
		} else {
			$age = [$i, $i.'期'.$class.'年生'];
		}
		if ($class > 0) {
			push(@ages, $age);
		}
	}
}

########################
# 現在のユーザー情報取得
sub getUserAge() {
	my @bind = ($session->param('userid'), '0');
	my $age = &selectFetch($dbh, 'SELECT age FROM users WHERE userid=? and deleteflag=?', @bind);
	return $age;
}

################
# 入力チェック
sub searchUser() {
	if ($msg) {
		return 0;
	}

	# 職業
	my $job = $cgi->param('job');
	$msg .= &checkString('職業', $job, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($job =~ /[\<\>\r\n]/) {
		$msg .= '職業に使用できない文字があります。';
		return 0;
	}

	# パート
	my $part = $cgi->param('part');
	$msg .= &checkString('パート', $part, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($part =~ /[\<\>\r\n]/) {
		$msg .= 'パートに使用できない文字があります。';
		return 0;
	}

	# 期
	my $age = $cgi->param('age');
	my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
	$now_year = $now_year + 1900;
	$now_month++;
	my $max_age = $now_year - 1976 + 3;
	if ($now_month >= 4) {
		$max_age ++;
	}
	if ($age && ($age < 1 || $age >= $max_age)) {
		$msg .= '期の値が不正です。'.$age;
		return 0;
	}

	# 検索実行
	my $pagesize = $cgi->param('size') + 0;
	if (!$pagesize) {
		$pagesize = 10; # デフォルトサイズ
	}
	my $pagestart = $cgi->param('start') + 0;
	my @bind = ('0');
	my $sqlcount = 'SELECT count(*)';
	my $sql = 'SELECT userid, name, job, part, age, note, registtime';
	my $sqlwhere = ' FROM users WHERE deleteflag=?';
	if ($job) {
		$sqlwhere .= ' and job LIKE ?';
		push(@bind, '%'.$job.'%');
	}
	if ($part) {
		$sqlwhere .= ' AND part LIKE ?';
		push(@bind, '%'.$part.'%');
	}
	if ($age) {
		$sqlwhere .= ' AND age=?';
		push(@bind, $age);
	}
	$sqlcount .= $sqlwhere;
	$sql .= $sqlwhere.' ORDER BY registtime DESC';

	@users = ();
	$usercount = &selectFetch($dbh, $sqlcount, @bind);
	if ($usercount >= $pagesize) {
		$sql .= ' LIMIT '.$pagestart.', '.$pagesize;
	}
	@users = &selectFetchArrayRef($dbh, $sql, @bind);
	
	if (@users == 0) {
		$msg .= 'メンバーが見つかりません。';
	}

	return 1;
}
