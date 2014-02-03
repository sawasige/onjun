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

$cgi = new CGI;
my $cginame = $cgi->url(-relative=>1); # ← この行が空文字になってしまう
my $tmpl = "hoge/$cginame.tmpl";
print $cgi->header(-charset=>'Shift_JIS');
print "$cginame\n";
print "$tmpl\n";

	# 設定読み込み
	%config = &config;

	# セッション取得
	my $check = 0;
	$session = &readSession;
	if (defined $session) {
		$sid = $session->id();
		$session->clear(['openurl']);
		$session->flush();
		# ログインしているならホームへ移動
		if ($session->param('userid')) {
			if (&isMobile()) {
				print $cgi->redirect("home.cgi?$config{'sessionname'}=$sid");
			} else {
				print $cgi->redirect('home.cgi');
			}
			$check = 1;
		}
	}

	if (!$check) {
		$dbh = &connectDB(1);

		# 現在の画面
		$msg .= &checkOnline($dbh, 0, 'トップページ');

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

	# メッセージ（あれば）
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

	# 1/10 の確率でセッション削除
	if (int(rand(10)) == 1) {
		&deleteOldSession();
	}
}

#################
# セッション削除
sub deleteOldSession {
	my @files = glob($config{'sessiondir'}.'/*');
	foreach my $file(@files) {
		my $lastmodified = (stat $file)[9];
		# 1日間経過したファイルは削除
		if ($lastmodified < time() - 60 * 60 * 24 * 1) {
			unlink($file);
		}
	}
}
