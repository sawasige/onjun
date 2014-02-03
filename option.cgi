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
			$check = &checkOption();
		}

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'オプション');

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

	my $mailmessageflag = '1';
	my $check = 1;
	if ($cgi->param('cancel')) {
		# メッセージお知らせメール
		$mailmessageflag = $session->param('mailmessageflag');
	} elsif ($cgi->param('submit')) {
		# メッセージお知らせメール
		$mailmessageflag = $cgi->param('mailmessageflag');
	} else {
		# メッセージお知らせメール
		my @bind = ($session->param('userid'));
		$mailmessageflag = &selectFetch($dbh, 'SELECT mailmessageflag FROM users WHERE userid=?', @bind);
	}
	
	if ($check) {
		if (($mailmessageflag eq '1' || $mailmessageflag eq 'on') && $tmpl->query(name => 'MAILMESSAGEFLAG') eq 'VAR') {
			$tmpl->param(MAILMESSAGEFLAG => 'checked');
		}
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
sub checkOption() {
	if ($msg) {
		return 0;
	}

	# メッセージお知らせメール
	my $mailmessageflag = $cgi->param('mailmessageflag');
	if ($mailmessageflag eq 'on') {
		$mailmessageflag = '1';
	} elsif (!$mailmessageflag) {
		$mailmessageflag = '0';
	} else {
		$msg .= 'メッセージお知らせメールの値が不正です。';
		return 0;
	};

	# 入力チェック成功！！
	$session->param('mailmessageflag', $mailmessageflag);
	$session->flush();
	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect('optionconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# セッションは Cookie 埋め込み
		print $cgi->redirect('optionconfirm.cgi');
	}

	return 1;
}

