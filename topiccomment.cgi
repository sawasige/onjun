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
my $topiccommentid = 0;
my $topiccommentbody = '';
my $topiccommentregistuserid = 0;
my $topiccommentregisttime = '';
my $topiccommentregistusername = '';

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
		$sid = $session->id;

		# DB オープン
		$dbh = &connectDB(1);

		# トピックコメント情報取得
		&getTopicCommentInfo();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'トピックコメント');

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

	# メッセージ
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();
	


	# トピックコメントが有効
	if ($topiccommentbody) {
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
		# トピックコメントID
		if ($tmpl->query(name => ['TOPICCOMMENTID']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTID => &convertOutput($topiccommentid));
		}
		# トピックコメント
		if ($tmpl->query(name => ['TOPICCOMMENTBODY']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTBODY => &convertOutput($topiccommentbody, 1));
		}

		# 登録時間
		if ($topiccommentregisttime && $tmpl->query(name => ['TOPICCOMMENTREGISTTIME']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTREGISTTIME => $topiccommentregisttime);
		}
		
		# 登録者
		if ($topiccommentregistusername && $tmpl->query(name => ['TOPICCOMMENTREGISTUSERNAME']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTREGISTUSERNAME => &convertOutput($topiccommentregistusername));
		}
		
		# 登録者URL
		if ($topiccommentregistuserid && $tmpl->query(name => ['TOPICCOMMENTREGISTUSERURL']) eq 'VAR') {
			my $url = 'profile.cgi?userid='.$topiccommentregistuserid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(TOPICCOMMENTREGISTUSERURL => &convertOutput($url));
		}

		# トピックコメント修正URL
		if (($session->param('userid') eq $topiccommentregistuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['MODIFYTOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'modifytopiccomment.cgi?topiccommentid='.$topiccommentid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MODIFYTOPICCOMMENTURL => &convertOutput($url));
		}
		# トピックコメント削除URL
		if (($session->param('userid') eq $topiccommentregistuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['DELETETOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'deletetopiccommentconfirm.cgi?topiccommentid='.$topiccommentid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(DELETETOPICCOMMENTURL => &convertOutput($url));
		}

		# コメントを書くURL
		if ($tmpl->query(name => ['POSTTOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'posttopiccomment.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(POSTTOPICCOMMENTURL => &convertOutput($url));
		}

		# 新規トピック作成URL
		if ($tmpl->query(name => ['URL_POSTTOPIC']) eq 'VAR') {
			my $url = 'posttopic.cgi?forumid='.$forumid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPIC => &convertOutput($url));
		}
	}

	# 添付ファイル1
	if ($tmpl->query(name => ['FILE1LARGEURL']) eq 'VAR') {
		my $lname1 = &getPublishFile('tc'.$topiccommentid.'_1');
		if ($lname1) {
			$tmpl->param(FILE1LARGEURL => $lname1);
			if ($tmpl->query(name => ['FILE1SMALLURL']) eq 'VAR') {
				my $sname1 = &getPublishFile('tc'.$topiccommentid.'_1_s');
				if ($sname1) {
					$tmpl->param(FILE1SMALLURL => $sname1);
				}
			}
		}
	}

	# 添付ファイル2
	if ($tmpl->query(name => ['FILE2LARGEURL']) eq 'VAR') {
		my $lname2 = &getPublishFile('tc'.$topiccommentid.'_2');
		if ($lname2) {
			$tmpl->param(FILE2LARGEURL => $lname2);
			if ($tmpl->query(name => ['FILE2SMALLURL']) eq 'VAR') {
				my $sname2 = &getPublishFile('tc'.$topiccommentid.'_2_s');
				if ($sname2) {
					$tmpl->param(FILE2SMALLURL => $sname2);
				}
			}
		}
	}

	# 添付ファイル3
	if ($tmpl->query(name => ['FILE3LARGEURL']) eq 'VAR') {
		my $lname3 = &getPublishFile('tc'.$topiccommentid.'_3');
		if ($lname3) {
			$tmpl->param(FILE3LARGEURL => $lname3);
			if ($tmpl->query(name => ['FILE3SMALLURL']) eq 'VAR') {
				my $sname3 = &getPublishFile('tc'.$topiccommentid.'_3_s');
				if ($sname3) {
					$tmpl->param(FILE3SMALLURL => $sname3);
				}
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

##########################
# トピックコメント情報取得
sub getTopicCommentInfo() {
	# トピックコメントID
	$topiccommentid = $cgi->param('topiccommentid');
	my $sql = 
		'SELECT a.forumid,'.
		' a.name,'.
		' a.note,'.
		' b.topicid,'.
		' b.title,'.
		' b.body,'.
		' c.body,'.
		' c.registuserid,'.
		' c.registtime,'.
		' d.name'.
		' FROM'.
		' forums a,'.
		' topics b,'.
		' topiccomments c,'.
		' users d'.
		' WHERE'.
		' a.forumid=b.forumid'.
		' AND b.topicid=c.topicid'.
		' AND c.registuserid=d.userid'.
		' AND c.topiccommentid=?'.
		' AND a.deleteflag=?'.
		' AND b.deleteflag=?'.
		' AND c.deleteflag=?'.
		' AND a.powerlevel<=?';
	my @bind = ($topiccommentid, '0', '0', '0', $session->param('powerlevel'));
	my ($fid, $fname, $fnote, $tid, $ttitle, $tbody, $cbody, $cuserid, $ctime, $uname) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topicid = $tid;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	$topiccommentbody = $cbody;
	$topiccommentregistuserid = $cuserid;
	$topiccommentregisttime = $ctime;
	$topiccommentregistusername = $uname;
	if (!$topiccommentbody) {
		$msg .= 'パラメータが不正です。';
	}
}

