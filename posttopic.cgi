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

		# DB オープン
		$dbh = &connectDB(1);

		# フォーラム情報取得
		&getForumInfo();

		# 登録
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &checkTopic();
		}

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), '新規トピック作成');

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

	# フォーラムが有効
	if ($forumname) {
		# メール送信ページURL
		if ($tmpl->query(name => ['MAILTOPICURL']) eq 'VAR') {
			my $url = 'mailtopic.cgi?forumid='.$forumid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MAILTOPICURL => &convertOutput($url));
		}

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

		my $title = '';
		my $body = '';
		my $check = 1;
		if ($cgi->param('cancel')) {
			$title = $session->param('title');
			$body = $session->param('body');
			if (!$title) {
				$msg .= 'トピックの情報が失われました。';
				$check = 0;
			}
		} elsif ($cgi->param('submit')) {
			$title = $cgi->param('title');
			$body = $cgi->param('body');
		}

		if ($check) {
			# タイトル
			if ($tmpl->query(name => 'TOPICTITLE') eq 'VAR') {
				$tmpl->param(TOPICTITLE => &convertOutput($title));
			}
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
# フォーラム情報取得
sub getForumInfo() {
	# フォーラムID
	if ($cgi->param('cancel')) {
		$forumid = $session->param('forumid');
	} else {
		$forumid = $cgi->param('forumid');
	}
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
# 入力チェック
sub checkTopic() {
	if ($msg) {
		return 0;
	}

	my %data;
	$data{'title'} = $cgi->param('title');
	$data{'body'} = $cgi->param('body');
	$data{'file1'} = $cgi->param('file1');
	$data{'file2'} = $cgi->param('file2');
	$data{'file3'} = $cgi->param('file3');
	$msg .= &postData($dbh, $forumid, 'tp', \%data, $sid);
	if ($msg) {
		return 0;
	}

	# 入力チェック成功！！
	$session->param('forumid', $forumid);
	$session->param('title', $data{'title'});
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
		print $cgi->redirect('posttopicconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# セッションは Cookie 埋め込み
		print $cgi->redirect('posttopicconfirm.cgi');
	}

	return 1;
}

