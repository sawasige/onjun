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
			$check = &checkMessage();
		}

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'メッセージ送信');

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

	my $replyid = 0;
	my $reply_name = '';
	my $reply_subject = '';
	my $reply_body = '';
	my $receiver_userid = 0;
	my $receiver_name = '';
	my $subject = '';
	my $body = '';
	my $check = 1;

	if ($cgi->param('cancel')) {
		$replyid = $session->param('replyid');
		$subject = $session->param('subject');
		$body = $session->param('body');
		if (!$subject) {
			$msg .= 'メッセージの情報が失われました。';
			$check = 0;
		}
	} else {
		$replyid = $cgi->param('replyid');
		$receiver_userid = $cgi->param('receiver_userid');
		$subject = $cgi->param('subject');
		$body = $cgi->param('body');
		if (!$replyid && !$receiver_userid) {
			$msg .= 'パラメータが不正です。';
			$check = 0;
		}
	}
	if ($check) {
		# 返信
		if ($replyid) {
			my ($source_sender_userid, $source_subject, $source_body) = &getMessageInfo($replyid);
			if ($source_sender_userid) {
				$receiver_userid = $source_sender_userid;
				$reply_subject = $source_subject;
				$reply_body = $source_body;
				$receiver_name = &getUserName($receiver_userid);
				if (!$receiver_name) {
					$msg .= '返信先のユーザーが存在しません。';
					$check = 0;
				}
			} else {
				$msg .= '返信するメッセージが存在しません。';
				$check = 0;
			}
			if (!$cgi->param('submit') && !$cgi->param('cancel')) {
				if ($reply_subject =~ /^Re\:/) {
					$subject = $reply_subject;
				} else {
					$subject = 'Re: '.$reply_subject;
				}
				my @lines = split(/\n/, $reply_body);
				$body = '';
				foreach my $line(@lines) {
					$body .= '> '.$line."\n";
				}
			}
		} else {
			if ($cgi->param('cancel')) {
				$receiver_userid = $session->param('receiver_userid');
			} else {
				$receiver_userid = $cgi->param('receiver_userid');
			}
			$receiver_name = &getUserName($receiver_userid);
			if (!$receiver_name) {
				$msg .= '送信先のユーザーが存在しません。';
				$check = 0;
			}
		}
	}
	if ($check) {
		# 返信ID
		if ($tmpl->query(name => 'REPLYID') eq 'VAR') {
			$tmpl->param(REPLYID => &convertOutput($replyid));
		}
		# 返信元サブジェクト
		if ($tmpl->query(name => 'REPLY_SUBJECT') eq 'VAR') {
			$tmpl->param(REPLY_SUBJECT => &convertOutput($reply_subject));
		}
		# 返信元本文
		if ($tmpl->query(name => 'REPLY_BODY') eq 'VAR') {
			$tmpl->param(REPLY_BODY => &convertOutput($reply_body, 1));
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
			$tmpl->param(BODY => &convertOutput($body));
		}

	}
	
	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}


#############################
# 返信元のメッセージ情報取得
sub getMessageInfo($) {
	my $replyid = shift;
	my $sql = 'SELECT sender_userid, subject, body FROM messages WHERE receiver_userid=? AND messageid=?';
	my @bind = ($session->param('userid'), $replyid);
	my @message = &selectFetchArray($dbh, $sql, @bind);
	if (@message) {
		return @message;
	}
	return 0;
}

#################
# ユーザー名取得
sub getUserName($) {
	my $userid = shift;
	my $sql = 'SELECT name FROM users WHERE userid=? and deleteflag=?';
	my @bind = ($userid, 0);
	my $user = &selectFetch($dbh, $sql, @bind);
	if ($user) {
		return $user;
	}
	return 0;
}

###############
# 入力チェック
sub checkMessage() {
	if ($msg) {
		return 0;
	}

	# 返信
	my $replyid = $cgi->param('replyid') + 0;
	if ($replyid) {
		my @bind = ($session->param('userid'), $replyid);
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE receiver_userid=? AND messageid=?', @bind);
		if (!$count) {
			$msg .= '返信先が不明です。';
			return 0;
		}
	}
	
	# 宛先
	my $receiver_userid = $cgi->param('receiver_userid') + 0;
	my $receiver_name = '';
	if ($receiver_userid) {
		my @bind = ($receiver_userid, 0);
		$receiver_name = &selectFetch($dbh, 'SELECT name FROM users WHERE userid=? AND deleteflag=?', @bind);
		if (!$receiver_name) {
			$msg .= '宛先が不明です。';
			return 0;
		}
	} else {
		$msg .= '宛先が不明です。';
		return 0;
	}
	
	# サブジェクト
	my $subject = $cgi->param('subject');
	$msg .= &checkString('サブジェクト', $subject, 255, 1);
	if ($msg) {
		return 0;
	}

	# 本文
	my $body = $cgi->param('body');
	$msg .= &checkString('本文', $body, 2000, 1);
	if ($msg) {
		return 0;
	}

	# 重複チェック
	my @bind = ($session->param('userid'), $receiver_userid, $subject, $body);
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE sender_userid=? AND receiver_userid=? AND subject=? AND body=? AND DATE_ADD(sendtime, INTERVAL 5 MINUTE) > now()', @bind);
	if ($count) {
		$msg .= '同じメッセージを続けて送信できません。';
		return 0;
	}

	# 入力チェック成功！！
	$session->param('replyid', $replyid);
	$session->param('receiver_userid', $receiver_userid);
	$session->param('receiver_name', $receiver_name);
	$session->param('subject', $subject);
	$session->param('body', $body);
	$session->flush();
	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect('sendmessageconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# セッションは Cookie 埋め込み
		print $cgi->redirect('sendmessageconfirm.cgi');
	}

	return 1;
}

