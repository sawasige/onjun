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
			$check = &checkValue();
		}

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'おんたまの開始');

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

	my $ontamaname = '';
	if ($cgi->param('cancel')) {
		$ontamaname = $session->param('ontamaname');
	} elsif ($cgi->param('submit')) {
		$ontamaname = $cgi->param('ontamaname');
	}
	
	if ($ontamaname && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
		$tmpl->param(ONTAMANAME => &convertOutput($ontamaname));
	}

	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}


###############
# 入力チェック
sub checkValue() {
	if ($msg) {
		return 0;
	}

	# メッセージお知らせメール
	my $ontamaname = $cgi->param('ontamaname');
	$msg .= &checkString('おんたまの名前', $ontamaname, 30, 1);
	if ($msg) {
		return 0;
	}

	# 入力チェック成功！！
	$session->param('ontamaname', $ontamaname);
	$session->flush();
	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect('setontamaconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# セッションは Cookie 埋め込み
		print $cgi->redirect('setontamaconfirm.cgi');
	}

	return 1;
}

