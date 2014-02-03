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

		# 登録
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &regUser();
		} elsif ($cgi->param('delete')) {
			$check = &delUser();
		}

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'かんたんログイン設定');

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

	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###############
# 機種情報登録
sub regUser() {
	my $key = &getPhoneID();
	if (!$key) {
		$msg .= '機種が判別できませんでした。';
		return 0;
	}

	# DB 登録
	my @bind = ($key, $session->param('userid'));
	my $sql = 
		'UPDATE users SET '.
		'mobcode=? '.
		'where userid=?';
	&doDB($dbh, $sql, @bind);

	$msg .= '機種情報を登録しました。';
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

###############
# 機種情報削除
sub delUser() {
	# DB 登録
	my @bind = ('', $session->param('userid'));
	my $sql = 
		'UPDATE users SET '.
		'mobcode=? '.
		'where userid=?';
	&doDB($dbh, $sql, @bind);

	$msg .= '機種情報を削除しました。';
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

