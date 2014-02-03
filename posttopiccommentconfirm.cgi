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
		
		# キャンセルなら戻る
		if ($cgi->param('cancel')) {
			# 画面リダイレクト
			if (&isMobile()) {
				# セッションは URL 埋め込み
				print $cgi->redirect("posttopiccomment.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("posttopiccomment.cgi?cancel=1");
			}
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# トピック情報取得
			&getTopicInfo();

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &writeComment();
			}

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'トピックコメント投稿確認');

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
		my $body = $session->param('body');
		my $fname1 = $session->param('fname1');
		my $fname2 = $session->param('fname2');
		my $fname3 = $session->param('fname3');

		# トピックが有効
		if ($topictitle) {
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

			# コメント
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
# トピック情報取得
sub getTopicInfo() {
	# トピックID
	$topicid = $session->param('topicid');
	
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

###################
# コメント書き込み
sub writeComment() {
	if ($msg) {
		return 0;
	}

	my %data;
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

	$msg .= &submitTopicComment($dbh, $topicid, \%data, $session->param('userid'));
	if ($msg) {
		return 0;
	}

	$msg .= 'コメントを書き込みました。';
	$session->clear(['topicid', 'body']);
	$session->param('msg', $msg);
	$session->flush();

	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("topic.cgi?topiccommentid=$data{'newtopiccommentid'}&$config{'sessionname'}=$sid#$data{'newtopiccommentid'}");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('topic.cgi?topiccommentid='.$data{'newtopiccommentid'}.'#'.$data{'newtopiccommentid'});
	}

	return 1;
}

