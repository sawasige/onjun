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
my %message = ();

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
			my $url = 'sendmessageview.cgi?messageid='.$cgi->param('messageid');
			if (&isMobile()) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			print $cgi->redirect($url);
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# 削除
			my $check = 0;
			if ($cgi->param('submit')) {
				$check =&deleteMessage();
			}

			if (!$check) {
				# メッセージ取得
				&getMessage();

				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), '送信済みメッセージ削除');

				# 画面表示
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

	if ($message{'subject'}) {
		# 宛先
		if ($tmpl->query(name => 'RECEIVER_NAME') eq 'VAR') {
			$tmpl->param(RECEIVER_NAME => &convertOutput($message{'receiver_name'}));
		}
		# 送信時間
		if ($tmpl->query(name => 'SENDTIME') eq 'VAR') {
			$tmpl->param(SENDTIME => &convertOutput($message{'sendtime'}));
		}
		# サブジェクト
		if ($tmpl->query(name => 'SUBJECT') eq 'VAR') {
			$tmpl->param(SUBJECT => &convertOutput($message{'subject'}));
		}
		# 本文
		if ($tmpl->query(name => 'BODY') eq 'VAR') {
			$tmpl->param(BODY => &convertOutput($message{'body'}, 1));
		}
		# メッセージ番号
		if ($tmpl->query(name => 'MESSAGEID') eq 'VAR') {
			$tmpl->param(MESSAGEID => $cgi->param('messageid'));
		}

	} else {
		$msg .= 'メッセージがありません。';
	}
	
	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

#################
# メッセージ取得
sub getMessage() {
	my $messageid = $cgi->param('messageid');
	if ($messageid) {
		my $sql = 'SELECT a.subject, a.body, a.sendtime, b.name FROM messages a, users b'.
			' WHERE a.receiver_userid=b.userid AND a.messageid=? AND a.sender_userid=? AND a.sender_deleteflag=?';
		my @bind = ($messageid, $session->param('userid'), 0);
		my ($subject, $body, $sendtime, $receiver_name) = &selectFetchArray($dbh, $sql, @bind);
		if ($subject) {
			$message{'subject'} = $subject;
			$message{'body'} = $body;
			$message{'receiver_name'} = $receiver_name;
			$message{'sendtime'} = $sendtime;
		}
	}
}

#################
# メッセージ削除
sub deleteMessage() {
	my $messageid = $cgi->param('messageid');
	if (!$messageid) {
		return 0;
	}
	my @bind = ('1', $messageid, $session->param('userid'));
	my $sql = 'UPDATE messages SET sender_deleteflag=? WHERE messageid=? AND sender_userid=?';
	&doDB($dbh, $sql, @bind);

	$msg .= '送信済みメッセージを削除しました。';

	$session->param('msg', $msg);
	$session->flush();

	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("sendmessagelist.cgi?$config{'sessionname'}=$sid");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('sendmessagelist.cgi');
	}

	return 1;
}

