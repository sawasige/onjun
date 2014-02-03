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
my $userid = 0;
my @ages = ();

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
		# セッション ID
		$sid = $session->id;

		# DB オープン
		$dbh = &connectDB(1);

		# 変更するユーザーID
		if ($session->param('powerlevel') >= 5) {
			$userid = $cgi->param('userid') || $session->param('userid');
		} else {
			$userid = $session->param('userid');
		}

		# 登録
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &regUser();
		}

		# 選択項目取得
		&getValues();

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'プロフィール修正');

			&disp;
		}

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

	my $user;
	my $pass;
	my $mail;
	my $realname;
	my $birthday;
	my $sex;
	my $blood;
	my $job;
	my $part;
	my $place;
	my $age;
	my $note;
	
	if ($cgi->param('submit')) {
		$user = $cgi->param('user');
		$pass = $cgi->param('pass');
		$mail = $cgi->param('mail');
		$realname = $cgi->param('realname');
		$birthday = $cgi->param('birthday');
		$sex = $cgi->param('sex');
		$blood = $cgi->param('blood');
		$job = $cgi->param('job');
		$part = $cgi->param('part');
		$place = $cgi->param('place');
		$age = $cgi->param('age');
		$note = $cgi->param('note');
	} elsif ($session->param('changeprofile')) {
		$session->clear(['changeprofile']);
		$session->flush();
		$user = $session->param('user');
		$pass = $session->param('pass');
		$mail = $session->param('mail');
		$realname = $session->param('realname');
		$birthday = $session->param('birthday');
		$sex = $session->param('sex');
		$blood = $session->param('blood');
		$job = $session->param('job');
		$part = $session->param('part');
		$place = $session->param('place');
		$age = $session->param('age');
		$note = $session->param('note');
	} else {
		my @userInfo = &getUserInfo();
		$user = $userInfo[0];
		$pass = $userInfo[1];
		$mail = $userInfo[2];
		$realname = $userInfo[3];
		$birthday = $userInfo[4];
		$sex = $userInfo[5];
		$blood = $userInfo[6];
		$job = $userInfo[7];
		$part = $userInfo[8];
		$place = $userInfo[9];
		$age = $userInfo[10];
		$note = $userInfo[11];
		$birthday =~ s/-//g;
		if ($birthday eq '00000000') {
			$birthday = '';
		}
	}

	# ユーザーID
	if ($tmpl->query(name => 'USERID') eq 'VAR') {
		$tmpl->param(USERID => $userid);
	}
	# ユーザー名
	if ($tmpl->query(name => 'USER') eq 'VAR') {
		$tmpl->param(USER => &convertOutput($user));
	}
	# パスワード
	if ($tmpl->query(name => 'PASS') eq 'VAR') {
		$tmpl->param(PASS => &convertOutput($pass));
	}
	# メール
	if ($tmpl->query(name => 'MAIL') eq 'VAR') {
		$tmpl->param(MAIL => &convertOutput($mail));
	}
	# 本名
	if ($tmpl->query(name => 'REALNAME') eq 'VAR') {
		$tmpl->param(REALNAME => &convertOutput($realname));
	}
	# 誕生日
	if ($tmpl->query(name => 'BIRTHDAY') eq 'VAR') {
		$tmpl->param(BIRTHDAY => &convertOutput($birthday));
	}
	# 性別
	if ($tmpl->query(name => 'SEX') eq 'LOOP') {
		$tmpl->param(SEX => [
			{
				SEXVALUE => '',
				SEXSELECTED => $sex eq '' && 'selected',
				SEXLABEL => '未選択'
			},
			{
				SEXVALUE => 'M',
				SEXSELECTED => $sex eq 'M' && 'selected',
				SEXLABEL => '男性'
			},
			{
				SEXVALUE => 'F',
				SEXSELECTED => $sex eq 'F' && 'selected',
				SEXLABEL => '女性'
			}
		]);
	}
	# 血液型
	if ($tmpl->query(name => 'BLOOD') eq 'LOOP') {
		$tmpl->param(BLOOD => [
			{
				BLOODVALUE => '',
				BLOODSELECTED => $blood eq '' && 'selected',
				BLOODLABEL => '未選択'
			},
			{
				BLOODVALUE => 'A',
				BLOODSELECTED => $blood eq 'a' && 'selected',
				BLOODLABEL => 'A型'
			},
			{
				BLOODVALUE => 'B',
				BLOODSELECTED => $blood eq 'B' && 'selected',
				BLOODLABEL => 'B型'
			},
			{
				BLOODVALUE => 'O',
				BLOODSELECTED => $blood eq 'O' && 'selected',
				BLOODLABEL => 'O型'
			},
			{
				BLOODVALUE => 'AB',
				BLOODSELECTED => $blood eq 'AB' && 'selected',
				BLOODLABEL => 'AB型'
			}
		]);
	}
	# 職業
	if ($tmpl->query(name => 'JOB') eq 'VAR') {
		$tmpl->param(JOB => &convertOutput($job));
	}
	# 楽器
	if ($tmpl->query(name => 'PART') eq 'VAR') {
		$tmpl->param(PART => &convertOutput($part));
	}
	# 住所
	if ($tmpl->query(name => 'PLACE') eq 'VAR') {
		$tmpl->param(PLACE => &convertOutput($place));
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

	# 自己紹介
	if ($tmpl->query(name => 'NOTE') eq 'VAR') {
		$tmpl->param(NOTE => &convertOutput($note));
	}

	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
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

####################
# ユーザー情報取得
sub getUserInfo() {
	my @bind = ($userid, '0');
	my @users = &selectFetchArray($dbh, 'SELECT name, pass, mail, realname, birthday, sex, blood, job, part, place, age, note FROM users WHERE userid=? and deleteflag=?', @bind);
	if (@users) {
		return @users;
	}
}

###############
# 入力チェック
sub regUser() {
	$session->param('changeprofile', 1);
	$session->flush();

	if ($msg) {
		return 0;
	}

	# ユーザー名
	my $user = $cgi->param('user');
	$msg .= &checkString('ユーザー名', $user, 30, 1);
	if ($msg) {
		return 0;
	}
	if ($user =~ /[\<\>\r\n]/) {
		$msg .= 'ユーザー名に使用できない文字があります。';
		return 0;
	}

	# パスワード
	my $pass = $cgi->param('pass');
	$msg .= &checkString('パスワード', $pass, 30, 1);
	if ($msg) {
		return 0;
	}

	# メール
	my $mail = $cgi->param('mail');
	$msg .= &checkString('メール', $mail, 60, 1);
	if ($msg) {
		return 0;
	}
	if ($mail !~ /^[\x01-\x7F]+@(([-a-z0-9]+\.)*[a-z]+|\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\])/) {
		$msg .= 'ありえないメールアドレスが入力されています。';
		return 0;
	}
	
	# 本名
	my $realname = $cgi->param('realname');
	$msg .= &checkString('本名', $realname, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($realname =~ /[\<\>\r\n]/) {
		$msg .= '本名に使用できない文字があります。';
		return 0;
	}

	# 誕生日
	my $birthday = $cgi->param('birthday');
	$msg .= &checkDateString('誕生日', $birthday, 0);
	if ($msg) {
		return 0;
	}

	# 性別
	my $sex = $cgi->param('sex');
	if ($sex && $sex ne 'M' && $sex ne 'F') {
		$msg .= '性別の値が不正です。';
		return 0;
	}

	# 血液型
	my $blood = $cgi->param('blood');
	if ($blood && $blood ne 'A' && $blood ne 'B' && $blood ne 'O' && $blood ne 'AB') {
		$msg .= '血液型の値が不正です。';
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

	# 楽器
	my $part = $cgi->param('part');
	$msg .= &checkString('パート', $part, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($part =~ /[\<\>\r\n]/) {
		$msg .= '楽器に使用できない文字があります。';
		return 0;
	}

	# 住所
	my $place = $cgi->param('place');
	$msg .= &checkString('パート', $place, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($place =~ /[\<\>\r\n]/) {
		$msg .= '住所に使用できない文字があります。';
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

	# 自己紹介
	my $note = $cgi->param('note');
	$msg .= &checkString('自己紹介', $note, 400, 0);
	if ($msg) {
		return 0;
	}

	# 重複チェック
	my @bind = ($userid, $user, '0');
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM users WHERE userid!=? AND name=? AND deleteflag=?', @bind);
	if ($count) {
		$msg .= '既に同じユーザー名が使われています。';
		return 0;
	}
	
	
	# 入力チェック成功！！

	$session->param('user', $user);
	$session->param('pass', $pass);
	$session->param('mail', $mail);
	$session->param('realname', $realname);
	$session->param('birthday', $birthday);
	$session->param('sex', $sex);
	$session->param('blood', $blood);
	$session->param('job', $job);
	$session->param('part', $part);
	$session->param('place', $place);
	$session->param('age', $age);
	$session->param('note', $note);
	$session->flush();
	# 画面リダイレクト
	my $url = 'profileconfirm.cgi?userid='.$userid;
	if (&isMobile()) {
		$url .= '&'.$config{'sessionname'}.'='.$sid;
	}
	print $cgi->redirect($url);

	return 1;
}

