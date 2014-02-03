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
my $topiccommentid = 0;
my $oldtopiccommentbody = '';

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

		# トピックコメント情報取得
		&getTopicCommentInfo();

		# 登録
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &checkTopicComment();
		}

		# 画面表示
		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'トピックコメント修正');

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

	# トピックコメントが有効
	if ($oldtopiccommentbody) {
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
		# 古いトピックコメント
		if ($tmpl->query(name => ['OLDTOPICCOMMENTBODY']) eq 'VAR') {
			$tmpl->param(OLDTOPICCOMMENTBODY => &convertOutput($oldtopiccommentbody, 1));
		}

		my $body = '';
		my $deletefile1 = '';
		my $deletefile2 = '';
		my $deletefile3 = '';
		my $check = 1;
		if ($cgi->param('cancel')) {
			$body = $session->param('body');
			$deletefile1 = $session->param('deletefile1');
			$deletefile2 = $session->param('deletefile2');
			$deletefile3 = $session->param('deletefile3');
			if (!$body) {
				$msg .= 'コメントの情報が失われました。';
				$check = 0;
			}
		} elsif ($cgi->param('submit')) {
			$body = $cgi->param('body');
			$deletefile1 = $cgi->param('deletefile1');
			$deletefile2 = $cgi->param('deletefile2');
			$deletefile3 = $cgi->param('deletefile3');
		} else {
			$body = $oldtopiccommentbody;
		}

		if ($check) {
			# 本文
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body));
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
					if ($deletefile1 && $tmpl->query(name => ['DELETEFILE1CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE1CHECKED => 'checked');
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
					if ($deletefile2 && $tmpl->query(name => ['DELETEFILE2CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE2CHECKED => 'checked');
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
					if ($deletefile3 && $tmpl->query(name => ['DELETEFILE3CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE3CHECKED => 'checked');
					}
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
	if ($cgi->param('cancel')) {
		$topiccommentid = $session->param('topiccommentid');
	} else {
		$topiccommentid = $cgi->param('topiccommentid');
	}
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
	$oldtopiccommentbody = $cbody;
	if (!$oldtopiccommentbody) {
		$msg .= 'パラメータが不正です。';
	}
}

###############
# 入力チェック
sub checkTopicComment() {
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
	my $deletefile1 = $cgi->param('deletefile1');
	my $deletefile2 = $cgi->param('deletefile2');
	my $deletefile3 = $cgi->param('deletefile3');

	# 入力チェック成功！！
	$session->param('topiccommentid', $topiccommentid);
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
	$session->param('deletefile1', $deletefile1);
	$session->param('deletefile2', $deletefile2);
	$session->param('deletefile3', $deletefile3);
	$session->flush();
	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect('modifytopiccommentconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# セッションは Cookie 埋め込み
		print $cgi->redirect('modifytopiccommentconfirm.cgi');
	}

	return 1;
}

