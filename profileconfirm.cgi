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
		
		# 修正するユーザーID
		if ($session->param('powerlevel') >= 5) {
			$userid = $cgi->param('userid') || $session->param('userid');
		} else {
			$userid = $session->param('userid');
		}

		# キャンセルなら戻る
		if ($cgi->param('cancel')) {
			# 画面リダイレクト
			my $url = 'editprofile.cgi?userid='.$userid;
			if (&isMobile()) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			print $cgi->redirect($url);
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &regUser();
			}

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'プロフィール修正確認');

				&disp;
			}
			
			# DB クローズ
			&disconnectDB($dbh);
		}
	}
	
}

###########
# 画面表示
sub disp {
	# テンプレート読み込み
	my $tmpl = &readTemplate($cgi);

	# 共通テンプレート変数セット
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	my $user = $session->param('user');
	my $pass = $session->param('pass');
	my $mail = $session->param('mail');
	my $realname = $session->param('realname');
	my $birthday = $session->param('birthday');
	my $sex = $session->param('sex');
	my $blood = $session->param('blood');
	my $job = $session->param('job');
	my $part = $session->param('part');
	my $place = $session->param('place');
	my $age = $session->param('age');
	my $note = $session->param('note');

	if ($user) {

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
		if ($tmpl->query(name => 'SEX') eq 'VAR') {
			if ($sex eq 'M') {
				$tmpl->param(SEX => '男性');
			} elsif ($sex eq 'F') {
				$tmpl->param(SEX => '女性');
			}
		}
		# 血液型
		if ($tmpl->query(name => 'BLOOD') eq 'VAR') {
			if ($blood eq 'A') {
				$tmpl->param(BLOOD => 'A型');
			} elsif ($blood eq 'B') {
				$tmpl->param(BLOOD => 'B型');
			} elsif ($blood eq 'O') {
				$tmpl->param(BLOOD => 'O型');
			} elsif ($blood eq 'AB') {
				$tmpl->param(BLOOD => 'AB型');
			}
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
		if ($tmpl->query(name => 'AGE') eq 'VAR') {
			if ($age) {
				my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
				$now_year = $now_year + 1900;
				$now_month++;
				my $year = $age + 1976;
				my $class = $now_year - $year + 3;
				if ($now_month >= 4) {
					$class++;
				}
				if ($class > 3) {
					$tmpl->param(AGE => $age.'期'.$year.'年卒業');
				} else {
					$tmpl->param(AGE => $age.'期'.$class.'年生');
				}
			}
		}

		# 自己紹介
		if ($tmpl->query(name => 'NOTE') eq 'VAR') {
			$tmpl->param(NOTE => &convertOutput($note, 1));
		}
	} else {
		$msg .= '修正中の情報が失われました。';
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


################
# ユーザー登録
sub regUser() {
	my $user = $session->param('user');
	my $pass = $session->param('pass');
	my $mail = $session->param('mail');
	my $realname = $session->param('realname');
	my $birthday = $session->param('birthday');
	my $sex = $session->param('sex');
	my $blood = $session->param('blood');
	my $job = $session->param('job');
	my $part = $session->param('part');
	my $place = $session->param('place');
	my $age = $session->param('age');
	my $note = $session->param('note');

	# 重複チェック
	my @bind = ($userid, $user, '0');
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM users WHERE userid!=? AND name=? AND deleteflag=?', @bind);
	if ($count) {
		$msg .= '既に同じユーザー名が使われています。';
		return 0;
	}

	# DB 登録
	my @bind = ($user, $pass, $mail, $realname, $birthday, $sex, $blood, $job, $part, $place, $age, $note, $userid);
	my $sql = 
		'UPDATE users SET '.
		'name = ?, '.
		'pass = ?, '.
		'mail = ?, '.
		'realname = ?, '.
		'birthday = ?, '.
		'sex = ?, '.
		'blood = ?, '.
		'job = ?, '.
		'part = ?, '.
		'place = ?, '.
		'age = ?, '.
		'note = ? '.
		'where userid = ?';
	&doDB($dbh, $sql, @bind);

	$msg .= 'プロフィールを修正しました。';
	$session->clear(['user', 'pass', 'mail', 'realname', 'birthday', 'sex', 'blood', 'job', 'part', 'place', 'age', 'note']);
	$session->param('msg', $msg);
	$session->flush();

	
	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("alert.cgi?$config{'sessionname'}=$sid");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('alert.cgi');
	}

	return 1;
}

