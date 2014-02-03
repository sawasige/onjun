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
		
		# キャンセルなら戻る
		if ($cgi->param('cancel')) {
			$topicid = $cgi->param('topicid');
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

			# トピック情報取得
			&getTopicInfo();

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &deleteTopic();
			}

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'トピック削除確認');

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
			if ($tmpl->query(name => ['BODY']) eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($topicbody, 1));
			}

			# 添付ファイル1
			if ($tmpl->query(name => ['FILE1LARGEURL']) eq 'VAR') {
				my $lname1 = &getPublishFile('tp'.$topicid.'_1');
				if ($lname1) {
					$tmpl->param(FILE1LARGEURL => $lname1);
					if ($tmpl->query(name => ['FILE1SMALLURL']) eq 'VAR') {
						my $sname1 = &getPublishFile('tp'.$topicid.'_1_s');
						if ($sname1) {
							$tmpl->param(FILE1SMALLURL => $sname1);
						}
					}
				}
			}

			# 添付ファイル2
			if ($tmpl->query(name => ['FILE2LARGEURL']) eq 'VAR') {
				my $lname2 = &getPublishFile('tp'.$topicid.'_2');
				if ($lname2) {
					$tmpl->param(FILE2LARGEURL => $lname2);
					if ($tmpl->query(name => ['FILE2SMALLURL']) eq 'VAR') {
						my $sname2 = &getPublishFile('tp'.$topicid.'_2_s');
						if ($sname2) {
							$tmpl->param(FILE2SMALLURL => $sname2);
						}
					}
				}
			}

			# 添付ファイル3
			if ($tmpl->query(name => ['FILE3LARGEURL']) eq 'VAR') {
				my $lname3 = &getPublishFile('tp'.$topicid.'_3');
				if ($lname3) {
					$tmpl->param(FILE3LARGEURL => $lname3);
					if ($tmpl->query(name => ['FILE3SMALLURL']) eq 'VAR') {
						my $sname3 = &getPublishFile('tp'.$topicid.'_3_s');
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
	# 管理者以外は書き込んだ当人のみ
	if ($session->param('powerlevel') < 5) {
		$sql .= ' AND b.registuserid=?';
		push(@bind, $session->param('userid'));
	}
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
# トピック削除
sub deleteTopic() {
	if ($msg) {
		return 0;
	}

	my $userid = $session->param('userid');

	# 管理者以外は書き込んだ当人のみ
	if ($session->param('powerlevel') < 5) {
		my @bind = ($topicid, $userid, '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topics WHERE topicid=? AND registuserid=? AND deleteflag=?', @bind);
		if (!$count) {
			$msg .= 'パラメータが不正です。';
			return 0;
		}
	} else {
		$userid = &selectFetch($dbh, 'SELECT registuserid FROM topics WHERE topicid=? AND deleteflag=?', ($topicid, '0'));
	}

	# DB 登録
	my @bind = ('1', $topicid);
	my $sql = 'UPDATE topics SET deleteflag=? WHERE topicid=?';
	&doDB($dbh, $sql, @bind);

	# ファイル削除
	&hideFile('tp'.$topicid);

	# 集計
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' topiccount=topiccount-1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	}

	# トピックコメントも削除
	$sql = 'SELECT topiccommentid, registuserid FROM topiccomments WHERE topicid=? AND deleteflag=?';
	my @comments = &selectFetchArrayRef($dbh, $sql, ($topicid, '0'));
	foreach my $row(@comments) {
		my ($topiccommentid, $registuserid) = @$row;
		# ファイル削除
		&hideFile('tc'.$topiccommentid);

		# 集計
		if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $registuserid)) {
			my $sql = 
				'UPDATE addup SET'.
				' topiccommentcount=topiccommentcount-1'.
				' WHERE'.
				' userid=?';
			my @bind = ($registuserid);
			&doDB($dbh, $sql, @bind);
		}
	}
	$sql = 'UPDATE topiccomments SET deleteflag=? WHERE topicid=?';
	@bind = ('1', $topicid);
	&doDB($dbh, $sql, @bind);

	$msg .= 'トピックを削除しました。';
	$session->param('msg', $msg);
	$session->flush();

	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("forum.cgi?forumid=$forumid&$config{'sessionname'}=$sid");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('forum.cgi?forumid='.$forumid);
	}

	return 1;
}

