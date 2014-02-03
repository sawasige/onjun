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
		
		# DB オープン
		$dbh = &connectDB(1);

		# メッセージ取得
		&getMessage();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), '受信メッセージ');

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

	if ($message{'subject'}) {
		# 送信者
		if ($tmpl->query(name => 'SENDER') eq 'VAR') {
			$tmpl->param(SENDER => &convertOutput($message{'sender_name'}));
		}
		# 送信者URL
		if ($tmpl->query(name => 'SENDERURL') eq 'VAR') {
			my $url = 'profile.cgi?userid='.$message{'sender_userid'};
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(SENDERURL => &convertOutput($url));
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
		# 返信 URL
		if ($tmpl->query(name => 'URL_REPLYMESSAGE') eq 'VAR') {
			my $url = 'sendmessage.cgi?replyid='.$cgi->param('messageid');
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			$tmpl->param(URL_REPLYMESSAGE => &convertOutput($url));
		}
		# 削除 URL
		if ($tmpl->query(name => 'URL_RECEIVEMESSAGEDELETE') eq 'VAR') {
			my $url = 'receivemessagedelete.cgi?messageid='.$cgi->param('messageid');
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			$tmpl->param(URL_RECEIVEMESSAGEDELETE => &convertOutput($url));
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
	my $opened = 0;
	if ($messageid) {
		my $sql = 'SELECT a.subject, a.body, a.sendtime, a.opentime, b.userid, b.name FROM messages a, users b'.
			' WHERE a.sender_userid=b.userid AND a.messageid=? AND a.receiver_userid=? AND a.receiver_deleteflag=?';
		my @bind = ($messageid, $session->param('userid'), 0);
		my ($subject, $body, $sendtime, $opentime, $sender_userid, $sender_name) = &selectFetchArray($dbh, $sql, @bind);
		$opentime =~ s/[^\d]//g;
		$opentime += 0;
		$opened = $opentime;
		if ($subject) {
			$message{'subject'} = $subject;
			$message{'body'} = $body;
			$message{'sender_userid'} = $sender_userid;
			$message{'sender_name'} = $sender_name;
			$message{'sendtime'} = $sendtime;
		}
	}

	if ($message{'subject'} && !$opened) {
		my @bind = ($messageid, $session->param('userid'));
		my $sql = 'UPDATE messages SET opentime=now() WHERE messageid=? AND receiver_userid=?';
		&doDB($dbh, $sql, @bind);
	}

}

