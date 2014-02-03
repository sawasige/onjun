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

		# フォーラム情報取得
		&getForumInfo();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'トピックメール投稿');

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

	# フォーラムが有効
	if ($forumname) {
		# フォーラムID
		if ($forumname && $tmpl->query(name => ['FORUMID']) eq 'VAR') {
			$tmpl->param(FORUMID => &convertOutput($forumid));
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
		if ($forumname && $tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($forumname));
		}
		# フォーラム説明
		if ($forumnote && $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
			$tmpl->param(FORUMNOTE => &convertOutput($forumnote, 1));
		}

		if ($tmpl->query(name => ['MAILTOTOPIC']) eq 'VAR' || 
			$tmpl->query(name => ['URL_RECEIVEMAIL']) eq 'VAR') {

			# メールキー
			my $mailkey = &getMailKey();

			# メール送信URL
			if ($tmpl->query(name => ['MAILTOTOPIC']) eq 'VAR') {
				my $subject = $mailkey;
				my $url = 'mailto:'.$config{'postmail'}.'?subject='.$subject;
				$tmpl->param(MAILTOTOPIC => &convertOutput($url));
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
		
		# 新規トピックURL
		if ($tmpl->query(name => ['URL_POSTTOPIC']) eq 'VAR') {
			my $url = 'posttopic.cgi?forumid='.$forumid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPIC => &convertOutput($url));
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
# フォーラム情報取得
sub getForumInfo() {
	$forumid = $cgi->param('forumid');
	my $sql = 
		'SELECT name, note'.
		' FROM forums'.
		' WHERE forumid=? AND deleteflag=? AND powerlevel<=?';
	my @bind = ($forumid, '0', $session->param('powerlevel'));
	my ($name, $note) = &selectFetchArray($dbh, $sql, @bind);
	$forumname = $name;
	$forumnote = $note;
	if (!$name) {
		$msg .= 'パラメータが不正です。';
	}
}

##############################
# メール投稿のサブジェクト生成
sub getMailKey() {

	# 重複チェック
	my @bind = ('0', 'tp', $forumid, $session->param('userid'));
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
		&doDB($dbh, $sql, ('tp', $forumid, $keystr, $session->param('userid')));
		$mailkeyid = &selectFetch($dbh, 'SELECT LAST_INSERT_ID()');
	}
	return 'post'.$mailkeyid.'_'.$keystr;
}

