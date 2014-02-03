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

	# セッション読み込み
	$sid = $cgi->cookie($config{'sessionname'}) || $cgi->param($config{'sessionname'}) || undef;
	$session = &readSession;

	# DB オープン
	$dbh = &connectDB(1);

	my $userid = 0;
	if (defined $session) {
		$userid = $session->param('userid') + 0;
		# 現在の画面
		$msg .= &checkOnline($dbh, $userid, 'ログアウト');
		&logout;
		$msg .= 'ログアウトしました。';
	} elsif ($sid) {
		# 現在の画面
		$msg .= &checkOnline($dbh, $userid, 'ログアウト');
		$msg .= '接続がタイムアウトしました。ログインからやり直してください。';
	} else {
		# 現在の画面
		$msg .= &checkOnline($dbh, $userid, 'ログアウト');
		$msg .= 'ログインしていません。';
	}


	# 画面表示
	&disp;

	# DB クローズ
	&disconnectDB($dbh);
}


##########
# 画面表示
sub disp
{
	# テンプレート読み込み
	my $tmpl = &readTemplate($cgi);

	# 共通テンプレート変数セット
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	# ユーザー
	if ($tmpl->query(name => 'USER') eq 'VAR') {
		$tmpl->param(USER => $cgi->param('user'));
	}

	# パスワード
	if ($tmpl->query(name => 'PASS') eq 'VAR') {
		$tmpl->param(PASS => $cgi->param('pass'));
	}

	# 簡単ログインフラグ
	if ($cgi->param('easylogin') && $tmpl->query(name => 'EASY') eq 'VAR') {
		$tmpl->param(EASY => $cgi->param('easylogin'));
	}

	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

#############
# ログアウト
sub logout {
	my $sql = 
		'UPDATE onlineusers SET deleteflag=? WHERE userid=?';
	&doDB($dbh, $sql, ('1', $session->param('userid') + 0));

	$session->close;
	$session->delete;
	$session = undef;
}
