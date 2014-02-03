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
my $oldtopictitle = '';
my $oldtopicbody = '';

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
				print $cgi->redirect("modifytopic.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("modifytopic.cgi?cancel=1");
			}
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# トピック情報取得
			&getTopicInfo();

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &modifyTopic();
			}

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'トピック修正確認');

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
		my $deletefile1 = $session->param('deletefile1');
		my $fname2 = $session->param('fname2');
		my $deletefile2 = $session->param('deletefile2');
		my $fname3 = $session->param('fname3');
		my $deletefile3 = $session->param('deletefile3');

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
			if ($tmpl->query(name => ['OLDTOPICTITLE']) eq 'VAR') {
				$tmpl->param(OLDTOPICTITLE => &convertOutput($oldtopictitle));
			}
			# トピック本文
			if ($tmpl->query(name => ['OLDTOPICBODY']) eq 'VAR') {
				$tmpl->param(OLDTOPICBODY => &convertOutput($oldtopicbody, 1));
			}

			# タイトル
			if ($tmpl->query(name => 'TOPICTITLE') eq 'VAR') {
				$tmpl->param(TOPICTITLE => &convertOutput($title));
			}
			# 本文
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body, 1));
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
					if ($deletefile1 && $tmpl->query(name => ['DELETEFILE1CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE1CHECKED => 'checked');
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
					if ($deletefile2 && $tmpl->query(name => ['DELETEFILE2CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE2CHECKED => 'checked');
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
					if ($deletefile3 && $tmpl->query(name => ['DELETEFILE3CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE3CHECKED => 'checked');
					}
				}
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
	# 管理者以外は書き込んだ当人のみ
	if ($session->param('powerlevel') < 5) {
		$sql .= ' AND b.registuserid=?';
		push(@bind, $session->param('userid'));
	}
	my ($fid, $fname, $fnote, $ttitle, $tbody) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$oldtopictitle = $ttitle;
	$oldtopicbody = $tbody;
	if (!$forumname) {
		$msg .= 'パラメータが不正です。';
	}
}

###############
# トピック修正
sub modifyTopic() {
	if ($msg) {
		return 0;
	}

	my $title = $session->param('title');
	my $body = $session->param('body');
	my $deletefile1 = $session->param('deletefile1');
	my $fname1 = $session->param('fname1');
	my $lname1 = $session->param('lname1');
	my $sname1 = $session->param('sname1');
	my $deletefile2 = $session->param('deletefile2');
	my $fname2 = $session->param('fname2');
	my $lname2 = $session->param('lname2');
	my $sname2 = $session->param('sname2');
	my $deletefile3 = $session->param('deletefile3');
	my $fname3 = $session->param('fname3');
	my $lname3 = $session->param('lname3');
	my $sname3 = $session->param('sname3');

	# 管理者以外は書き込んだ当人のみ
	if ($session->param('powerlevel') < 5) {
		my @bind = ($topicid, $session->param('userid'), '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topics WHERE topicid=? AND registuserid=? AND deleteflag=?', @bind);
		if (!$count) {
			$msg .= 'パラメータが不正です。';
			return 0;
		}
	}

	# コメント数（念のため）
	my $commentcount = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE deleteflag=? AND topicid=?', ('0', $topicid));

	# DB 登録
	my @bind = ($title, $body, $commentcount, $topicid);
	my $sql = 
		'UPDATE topics SET'.
		' title=?,'.
		' body=?,'.
		' commentcount=?'.
		' where topicid=?';

	&doDB($dbh, $sql, @bind);

	# 旧ファイルを削除
	if ($lname1 || $deletefile1) {
		&deleteFile('tp'.$topicid.'_1');
	}
	if ($lname2 || $deletefile2) {
		&deleteFile('tp'.$topicid.'_2');
	}
	if ($lname3 || $deletefile3) {
		&deleteFile('tp'.$topicid.'_3');
	}
	
	if (&publishFile($lname1, 'tp'.$topicid.'_1')) {
		&publishFile($sname1, 'tp'.$topicid.'_1_s');
	}
	if (&publishFile($lname2, 'tp'.$topicid.'_2')) {
		&publishFile($sname2, 'tp'.$topicid.'_2_s');
	}
	if (&publishFile($lname3, 'tp'.$topicid.'_3')) {
		&publishFile($sname3, 'tp'.$topicid.'_3_s');
	}

	$msg .= 'トピックを修正しました。';
	$session->clear(['topicid', 'title', 'body']);
	$session->param('msg', $msg);
	$session->flush();

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

