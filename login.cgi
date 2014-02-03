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

#プログラム開始
&main;

##########
# メイン
sub main {
	$cgi = new CGI;
	$msg = '';

	# 設定読み込み
	%config = &config;

	# セッション取得
	$session = &readSession;
	if (defined $session) {
		$sid = $session->id();
	}

	$dbh = &connectDB(1);

	# ログイン
	my $login = 0;
	if ($cgi->param('login') || $cgi->param('easylogin')) {
		$login = &login;
	}
	
	# 画面表示
	if (!$login) {
		&disp;
	}

	&disconnectDB($dbh);
}

###########
# 画面表示
sub disp {
	# テンプレート読み込み
	my $tmpl = &readTemplate($cgi);

	if ($session) {
		$msg .= $session->param('msg');
		$session->clear(['msg']);
		$session->flush();
	}

	# 共通テンプレート変数セット
	$msg .= &setCommonVars($tmpl, $session, $dbh);
	
	# メッセージ（あれば）
	my $phone = &getPhone();
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	if (&isMobile) {
		print $cgi->header(-charset=>'Shift_JIS');
	} else {
		print $cgi->header(
			-charset=>'Shift_JIS',
			-cookie=>$cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id));
	}
	print $tmpl->output;
}


###########
# ログイン
sub login {
	my $login = 0;
	my ($userid, $name, $powerlevel);
	if ($cgi->param('login')) {
		if (!$cgi->param('user')) {
			$msg .= 'ユーザー名を指定してください。';
		} elsif (!$cgi->param('pass')) {
			$msg .= 'パスワードを指定してください。';
		} else {
			my @bind = ($cgi->param('user'), $cgi->param('pass'), '0');
			my @users = &selectFetchArray($dbh, 'SELECT userid, name, powerlevel FROM users WHERE name=? AND pass=? AND deleteflag=?', @bind);
			if (@users) {
				$userid = $users[0];
				$name = $users[1];
				$powerlevel = $users[2];
				$login = 1;
			} else {
				$msg .= 'ユーザー名、またはパスワードが違います。';
			}
		}
	} elsif ($cgi->param('easylogin')) {
		# 携帯判別
		my $key = &getPhoneID();

		if ($key){
			my @bind = ($key, '0');
			my @users = &selectFetchArray($dbh, 'SELECT userid, name, powerlevel FROM users WHERE mobcode=? AND deleteflag=?', @bind);
			if (@users) {
				$userid = $users[0];
				$name = $users[1];
				$powerlevel = $users[2];
				$login = 1;
			} else {
				$msg .= 'お使いの機種は未登録です。通常通りログインしてください。';
			}
		} else {
			$msg .= '機種が判別できませんでした。';
		}
	} else {
		die;
	}
	
	# ログイン成功処理
	if ($login) {
		&writeLog(3, $name.'ログイン');

		$session->param('userid', $userid);
		$session->param('powerlevel', $powerlevel);
		$session->param('info', $name.'さんようこそ♪');
		$session->flush();
		# ログイン時間記録
		&doDB($dbh, 'UPDATE users SET useragent=?, lasttime=now() WHERE userid=?', ($ENV{'HTTP_USER_AGENT'}, $userid));

		my $url = '';
		if ($session->param('openurl')) {
			$url = $session->param('openurl');
			$session->clear(['openurl']);
			$session->flush();
		} else {
			$url = 'home.cgi'
		}

		# 画面リダイレクト
		if (&isMobile()) {
			if ($url =~ /\?/) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id();
			} else {
				$url .= '?'.$config{'sessionname'}.'='.$session->id();
			}
			print $cgi->redirect($url);
		} elsif ($cgi->param('saveuser')) {
			my $cookie1 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id);
			my $cookie2 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>'user', -value=>$name, -expires=>'+1y');
			print $cgi->redirect(
				-uri=>$url,
				-cookie=>[$cookie1, $cookie2]);
		} else {
			my $cookie1 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id);
			my $cookie2 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>'user', -value=>'', -expires=>'-1d');
			print $cgi->redirect(
				-uri=>$url,
				-cookie=>[$cookie1, $cookie2]);
		}
	}
	
	return $login;
}

