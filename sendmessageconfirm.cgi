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
				print $cgi->redirect("sendmessage.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("sendmessage.cgi?cancel=1");
			}
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &sendMessage();
			}

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'メッセージ送信確認', $session->param('receiver_userid') + 0);

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

	if (!$msg) {
		my $replyid = $session->param('replyid');
		my $receiver_userid = $session->param('receiver_userid');
		my $receiver_name= $session->param('receiver_name');
		my $subject = $session->param('subject');
		my $body = $session->param('body');

		if ($receiver_userid) {
			# 返信ID
			if ($tmpl->query(name => 'REPLYID') eq 'VAR') {
				$tmpl->param(REPLYID => &convertOutput($replyid));
			}

			# 宛先ID
			if ($tmpl->query(name => 'RECEIVER_USERID') eq 'VAR') {
				$tmpl->param(RECEIVER_USERID => &convertOutput($receiver_userid));
			}
			# 宛先名前
			if ($tmpl->query(name => 'RECEIVER_NAME') eq 'VAR') {
				$tmpl->param(RECEIVER_NAME => &convertOutput($receiver_name));
			}
			# サブジェクト
			if ($tmpl->query(name => 'SUBJECT') eq 'VAR') {
				$tmpl->param(SUBJECT => &convertOutput($subject));
			}
			# 本文
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body, 1));
			}

		} else {
			$msg .= 'メッセージの情報が失われました。';
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
sub sendMessage() {
	my $userid = $session->param('userid');
	my $replyid = $session->param('replyid');
	my $receiver_userid = $session->param('receiver_userid');
	my $receiver_name;
	my $subject = $session->param('subject');
	my $body = $session->param('body');
	my $mailmessageflag;
	my $mailaddress;

	# データチェック
	if ($receiver_userid) {
		my @bind = ($receiver_userid, 0);
		my ($name, $address, $flag) = &selectFetchArray($dbh, 'SELECT name, mail, mailmessageflag FROM users WHERE userid=? AND deleteflag=?', @bind);
		$receiver_name = $name;
		$mailaddress = $address;
		$mailmessageflag = $flag;
		if (!$receiver_name) {
			$msg .= '宛先が不明です。';
			return 0;
		}
	} else {
		$msg .= 'メッセージの情報が失われました。';
		return 0;
	}

	# 重複チェック
	my @bind = ($userid, $receiver_userid, $subject, $body);
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE sender_userid=? AND receiver_userid=? AND subject=? AND body=? AND DATE_ADD(sendtime, INTERVAL 5 MINUTE) * 60 > now()', @bind);
	if ($count) {
		$msg .= '同じメッセージを続けて送信できません。';
		return 0;
	}

	# DB 登録
	my @bind = ($replyid, $userid, $receiver_userid, $subject, $body);
	my $sql = 
		'INSERT INTO messages('.
		'replyid, '.
		'sender_userid, '.
		'receiver_userid, '.
		'subject, '.
		'body, '.
		'sendtime '.
		') VALUES (?, ?, ?, ?, ?, now())';

	&doDB($dbh, $sql, @bind);

	$msg .= $receiver_name.'さん宛にメッセージを送信しました。';
	$session->clear(['replyid', 'receiver_userid', 'receiver_name', 'subject', 'body']);
	$session->param('msg', $msg);
	$session->flush();

	# メール送信
	if ($mailmessageflag) {
		my @bind = ($userid, 0);
		my $sender_name = &selectFetch($dbh, 'SELECT name FROM users WHERE userid=? AND deleteflag=?', @bind);
		my $sub = '【'.$config{'title'}.'】'.$sender_name.'さんからメッセージが届いています';
		my $body =  <<END;
$receiver_name さん、こんにちは。
$config{'title'} からのお知らせです。

$receiver_name さん宛に $sender_name さんからメッセージが届いています。

メッセージの内容を確認するには以下の URL をクリックしてください。

$config{'receivemessagelist_url'}

※このメールには返信できません。
END
		&sendMail($config{'adminmail'}, $mailaddress, $sub, $body, $config{'title'}, $receiver_name);
	}

	# 集計
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' messagecount=messagecount+1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	} else {
		my $sql = 
			'INSERT addup ('.
			' userid,'.
			' messagecount,'.
			' topiccount,'.
			' topiccommentcount'.
			') VALUES (?, ?, ?, ?)';
		my @bind = ($userid, 1, 0, 0);
		&doDB($dbh, $sql, @bind);
	}

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

