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
				print $cgi->redirect("topic.cgi?topicid=$topicid&$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("topic.cgi?topicid=$topicid");
			}
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# トピックコメント情報取得
			&getTopicCommentInfo();
			

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &deleteTopicComment();
			}

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'トピックコメント削除確認');

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

##########################
# トピックコメント情報取得
sub getTopicCommentInfo() {
	# トピックID
	$topiccommentid = $cgi->param('topiccommentid');
	
	my $sql = 
		'SELECT a.forumid, a.name, a.note, b.topicid, b.title, b.body, c.body'.
		' FROM forums a, topics b, topiccomments c'.
		' WHERE a.forumid=b.forumid AND b.topicid=c.topicid AND c.topiccommentid=? AND a.deleteflag=? AND b.deleteflag=? AND c.deleteflag=? AND a.powerlevel<=?';
	my @bind = ($topiccommentid, '0', '0', '0', $session->param('powerlevel'));
	# 管理者以外は書き込んだ当人のみ
	if ($session->param('powerlevel') < 5) {
		$sql .= ' AND c.registuserid=?';
		push(@bind, $session->param('userid'));
	}
	my ($fid, $fname, $fnote, $tid, $ttitle, $tbody, $cbody) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topicid = $tid;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	$topiccommentbody = $cbody;
	if (!$topiccommentbody) {
		$msg .= 'パラメータが不正です。';
	}
}

###############
# トピック修正
sub deleteTopicComment() {
	if ($msg) {
		return 0;
	}

	my $userid = $session->param('userid');
	
	# 管理者以外は書き込んだ当人のみ
	if ($session->param('powerlevel') < 5) {
		my @bind = ($topiccommentid, $userid, '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE topiccommentid=? AND registuserid=? AND deleteflag=?', @bind);
		if (!$count) {
			$msg .= 'パラメータが不正です。';
			return 0;
		}
	} else {
		$userid = &selectFetch($dbh, 'SELECT registuserid FROM topiccomments WHERE topiccommentid=? AND deleteflag=?', ($topiccommentid, '0'));
	}

	# DB 登録
	my @bind = ('1', $topiccommentid);
	my $sql = 'UPDATE topiccomments SET deleteflag=? WHERE topiccommentid=?';
	&doDB($dbh, $sql, @bind);

	my $lastcommentid = &selectFetch($dbh, 'SELECT max(topiccommentid) FROM topiccomments WHERE deleteflag=? AND topicid=?', ('0', $topicid));
	if ($lastcommentid) {
		my $commentcount = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE deleteflag=? AND topicid=?', ('0', $topicid));
		my ($lastuserid, $lasttime) = &selectFetchArray($dbh, 'SELECT registuserid, registtime FROM topiccomments WHERE topiccommentid=?', ($lastcommentid));
		&doDB($dbh, 'UPDATE topics SET lastcommentid=?, lastuserid=?, lasttime=?, commentcount=? WHERE topicid=?', ($lastcommentid, $lastuserid, $lasttime, $commentcount, $topicid));
	} else {
		my ($lastuserid, $lasttime) = &selectFetchArray($dbh, 'SELECT registuserid, registtime FROM topics WHERE topicid=?', ($topicid));
		&doDB($dbh, 'UPDATE topics SET lastcommentid=?, lastuserid=?, lasttime=? , commentcount=? WHERE topicid=?', (0, $lastuserid, $lasttime, 0, $topicid));
	}

	# ファイル削除
	&hideFile('tc'.$topiccommentid);

	$msg .= 'コメントを削除しました。';
	$session->param('msg', $msg);
	$session->flush();

	# 集計
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' topiccommentcount=topiccommentcount-1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	}

	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("topic.cgi?topicid=$topicid&$config{'sessionname'}=$sid");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('topic.cgi?topicid='.$topicid);
	}

	return 1;
}

