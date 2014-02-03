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

		# DB オープン
		$dbh = &connectDB(1);

		# トピック情報取得
		&getTopicInfo();

		# 登録
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &checkComment();
		}

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'トピックコメント投稿');

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

		my $body = '';
		my $check = 1;
		if ($cgi->param('cancel')) {
			$body = $session->param('body');
			if (!$body) {
				$msg .= 'コメントの情報が失われました。';
				$check = 0;
			}
		} elsif ($cgi->param('submit')) {
			$body = $cgi->param('body');
		}

		if ($check) {
			# 本文
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body));
			}
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
	if ($cgi->param('cancel')) {
		$topicid = $session->param('topicid');
	} else {
		$topicid = $cgi->param('topicid');
	}
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

###############
# 入力チェック
sub checkComment() {
	if ($msg) {
		return 0;
	}

	my %data;
	$data{'body'} = $cgi->param('body');
	$data{'file1'} = $cgi->param('file1');
	$data{'file2'} = $cgi->param('file2');
	$data{'file3'} = $cgi->param('file3');
	$msg .= &postData($dbh, $topicid, 'tc', \%data, $sid);
	if ($msg) {
		return 0;
	}

	# 入力チェック成功！！
	$session->param('topicid', $topicid);
	$session->param('body', $data{'body'});
	$session->param('fname1', $data{'fname1'});
	$session->param('lname1', $data{'lname1'});
	$session->param('sname1', $data{'sname1'});
	$session->param('fname2', $data{'fname2'});
	$session->param('lname2', $data{'lname2'});
	$session->param('sname2', $data{'sname2'});
	$session->param('fname3', $data{'fname3'});
	$session->param('lname3', $data{'lname3'});
	$session->param('sname3', $data{'sname3'});
	$session->flush();

	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect('posttopiccommentconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# セッションは Cookie 埋め込み
		print $cgi->redirect('posttopiccommentconfirm.cgi');
	}

	return 1;
}

