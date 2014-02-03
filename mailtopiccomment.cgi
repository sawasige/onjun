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
my $forumid = 0;
my $forumname = '';
my $forumnote = '';
my $topicid = 0;
my $topictitle = '';
my $topicbody = '';

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

		# トピック情報取得
		&getTopicInfo();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'トピックコメントメール投稿');

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

	# トピックが有効
	if ($topictitle) {
		# メール送信ページURL
		if ($tmpl->query(name => ['MAILTOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'mailtopiccomment.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MAILTOPICCOMMENTURL => &convertOutput($url));
		}

		# フォーラムID
		if ($tmpl->query(name => ['FORUMID']) eq 'VAR') {
			$tmpl->param(FORUMID => $forumid);
		}
		# フォーラムURL
		if ($tmpl->query(name => ['FORUMURL']) eq 'VAR') {
			my $url = 'forum.cgi?forumid='.$forumid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(FORUMURL => &convertOutput($url));
		}
		# フォーラム名
		if ($tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($forumname));
		}
		# フォーラム説明
		if ($tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
			$tmpl->param(FORUMNOTE => &convertOutput($forumnote, 1));
		}
		# トピックID
		if ($tmpl->query(name => ['TOPICID']) eq 'VAR') {
			$tmpl->param(TOPICID => $topicid);
		}
		# トピックURL
		if ($tmpl->query(name => ['TOPICURL']) eq 'VAR') {
			my $url = 'topic.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(TOPICURL => &convertOutput($url));
		}
		# トピックタイトル
		if ($tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
			$tmpl->param(TOPICTITLE => &convertOutput($topictitle));
		}
		# トピック本文
		if ($tmpl->query(name => ['TOPICBODY']) eq 'VAR') {
			$tmpl->param(TOPICBODY => &convertOutput($topicbody, 1));
		}

		if ($tmpl->query(name => ['MAILTOTOPICCOMMENT']) eq 'VAR' || 
			$tmpl->query(name => ['URL_RECEIVEMAIL']) eq 'VAR') {

			# メールキー
			my $mailkey = &getMailKey();

			# メール送信URL
			if ($tmpl->query(name => ['MAILTOTOPICCOMMENT']) eq 'VAR') {
				my $subject = $mailkey;
				my $url = 'mailto:'.$config{'postmail'}.'?subject='.$subject;
				$tmpl->param(MAILTOTOPICCOMMENT => &convertOutput($url));
			}

			# メール投稿確認の URL
			if ($tmpl->query(name => 'URL_RECEIVEMAIL') eq 'VAR') {
				my $url = 'receivemail.cgi?mailkey='.$mailkey;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(URL_RECEIVEMAIL => &convertOutput($url));
			}
			
		}

		# コメントを書く URL
		if ($tmpl->query(name => ['URL_POSTTOPICCOMMENT']) eq 'VAR') {
			my $url = 'posttopiccomment.cgi?topicid='.$topicid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPICCOMMENT => &convertOutput($url));
		}
	}
	
	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

####################
# トピック情報取得
sub getTopicInfo() {
	# トピックID
	$topicid = $cgi->param('topicid');
	
	my $sql = 
		'SELECT a.forumid, a.name, a.note, b.title, b.body'.
		' FROM forums a, topics b'.
		' WHERE a.forumid=b.forumid AND b.topicid=? AND a.deleteflag=? AND b.deleteflag=? AND a.powerlevel<=?';
	my @bind = ($topicid, '0', '0', $session->param('powerlevel'));
	my ($fid, $fname, $fnote, $ttitle, $tbody) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	if (!$forumname) {
		$msg .= 'パラメータが不正です。';
	}
}


##############################
# メール投稿のサブジェクト生成
sub getMailKey() {

	# 重複チェック
	my @bind = ('0', 'tc', $topicid, $session->param('userid'));
	my ($mailkeyid, $keystr) = &selectFetchArray($dbh, 'SELECT mailkeyid, keystr FROM mailkeys WHERE deleteflag=? AND kind=? AND id=? AND registuserid=?', @bind);
	if (!$mailkeyid) {
		$keystr = &getRandomString(5);
		my $sql = 
			'INSERT INTO mailkeys('.
			' kind,'.
			' id,'.
			' keystr,'.
			' registuserid,'.
			' registtime'.
			') VALUES (?, ?, ?, ?, now())';
		&doDB($dbh, $sql, ('tc', $topicid, $keystr, $session->param('userid')));
		$mailkeyid = &selectFetch($dbh, 'SELECT LAST_INSERT_ID()');
	}
	return 'post'.$mailkeyid.'_'.$keystr;
}

