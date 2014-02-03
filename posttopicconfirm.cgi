#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './post.pl';
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
		
		# キャンセルなら戻る
		if ($cgi->param('cancel')) {
			# 画面リダイレクト
			if (&isMobile()) {
				# セッションは URL 埋め込み
				print $cgi->redirect("posttopic.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("posttopic.cgi?cancel=1");
			}
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# フォーラム情報取得
			&getForumInfo();

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &createTopic();
			}

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), '新規トピック作成確認');

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
		my $title = $session->param('title');
		my $body = $session->param('body');
		my $fname1 = $session->param('fname1');
		my $fname2 = $session->param('fname2');
		my $fname3 = $session->param('fname3');

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

			# タイトル
			if ($tmpl->query(name => 'TOPICTITLE') eq 'VAR') {
				$tmpl->param(TOPICTITLE => &convertOutput($title));
			}

			# 本文
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body, 1));
			}

			# 写真1
			if ($tmpl->query(name => 'FILE1') eq 'VAR') {
				$tmpl->param(FILE1 => &convertOutput($fname1));
			}

			# 写真2
			if ($tmpl->query(name => 'FILE2') eq 'VAR') {
				$tmpl->param(FILE2 => &convertOutput($fname2));
			}

			# 写真3
			if ($tmpl->query(name => 'FILE3') eq 'VAR') {
				$tmpl->param(FILE3 => &convertOutput($fname3));
			}

		} else {
			$msg .= 'トピックの情報が失われました。';
		}
	}
	
	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => &convertOutput($msg));
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

####################
# フォーラム情報取得
sub getForumInfo() {
	# フォーラムID
	$forumid = $session->param('forumid');

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

###############
# トピック作成
sub createTopic() {
	if ($msg) {
		return 0;
	}

	my %data;
	$data{'title'} = $session->param('title');
	$data{'body'} = $session->param('body');
	$data{'fname1'} = $session->param('fname1');
	$data{'lname1'} = $session->param('lname1');
	$data{'sname1'} = $session->param('sname1');
	$data{'fname2'} = $session->param('fname2');
	$data{'lname2'} = $session->param('lname2');
	$data{'sname2'} = $session->param('sname2');
	$data{'fname3'} = $session->param('fname3');
	$data{'lname3'} = $session->param('lname3');
	$data{'sname3'} = $session->param('sname3');

	$msg .= &submitTopic($dbh, $forumid, \%data, $session->param('userid'));
	if ($msg) {
		return 0;
	}
	
	$msg .= '新しいトピックを生成しました。';
	$session->clear(['forumid', 'title', 'body', 'fname1', 'lname1', 'sname1', 'fname2', 'lname2', 'sname2', 'fname3', 'lname3', 'sname3']);
	$session->param('msg', $msg);
	$session->flush();

	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("topic.cgi?topicid=$data{'newtopicid'}&$config{'sessionname'}=$sid");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('topic.cgi?topicid='.$data{'newtopicid'});
	}

	return 1;
}

