#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './mail.pl';
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
		
		# キャンセルなら戻る
		if ($cgi->param('cancel')) {
			# 画面リダイレクト
			if (&isMobile()) {
				# セッションは URL 埋め込み
				print $cgi->redirect("option.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("option.cgi?cancel=1");
			}
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &registOption();
			}
			
			# DB クローズ
			&disconnectDB($dbh);

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'オプション確認');

				&disp;
			}
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

	if (!$msg) {
		my $mailmessageflag = $session->param('mailmessageflag');

		if ($mailmessageflag eq '1' && $tmpl->query(name => 'MAILMESSAGEFLAG') eq 'VAR') {
			$tmpl->param(MAILMESSAGEFLAG => $mailmessageflag);
		}
	}
	
	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

#################
# メッセージ送信
sub registOption() {
	my $mailmessageflag = $session->param('mailmessageflag');

	# データチェック
	if ($mailmessageflag ne '0' && $mailmessageflag ne '1') {
		$msg .= 'メッセージお知らせメールの値が不正です。';
		return 0;
	}

	# DB 登録
	my @bind = ($mailmessageflag, $session->param('userid'));
	my $sql = 
		'UPDATE users SET '.
		'mailmessageflag = ? '.
		'where userid = ?';

	&doDB($dbh, $sql, @bind);

	$msg .= '設定を変更しました。';
	$session->clear(['mailmessageflag']);
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

