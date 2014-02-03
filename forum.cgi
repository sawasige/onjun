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
my $topiccount = 0;
my @topics = ();
my $start = 0;
my $size = 10;

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

		# トピック一覧取得
		&getTopicList();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'フォーラム');

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

	# 新規トピック作成URL
	if ($tmpl->query(name => ['URL_POSTTOPIC']) eq 'VAR') {
		my $url = 'posttopic.cgi?forumid='.$forumid;
		if (&isMobile) {
			$url .= '&'.$config{'sessionname'}.'='.$session->id;
		}
		$tmpl->param(URL_POSTTOPIC => &convertOutput($url));
	}

	if ($tmpl->query(name => ['FORUMNAME']) eq 'VAR' || $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
		my $sql = 
			'SELECT name, note'.
			' FROM forums'.
			' WHERE forumid=? AND deleteflag=? AND powerlevel<=?';
		my @bind = ($forumid, '0', $session->param('powerlevel'));
		my ($name, $note) = &selectFetchArray($dbh, $sql, @bind);
		# フォーラム名
		if ($name && $tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($name));
		}
		# フォーラム説明
		if ($note && $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
			$tmpl->param(FORUMNOTE => &convertOutput($note, 1));
		}
	}

	# トピック一覧
	if (@topics && $tmpl->query(name => 'TOPICS') eq 'LOOP') {
		my @topicvars = ();
		foreach my $row(@topics) {
			my ($topicid, $title, $registtime, $lasttime, $registuserid, $registusername, $lastuserid, $lastusername, $commentcount) = @$row;
			my %topic;
			# トピックURL
			if ($tmpl->query(name => ['TOPICS', 'URL']) eq 'VAR') {
				my $url = 'topic.cgi?topicid='.$topicid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$topic{URL} = &convertOutput($url);
			}
			# トピックID
			if ($tmpl->query(name => ['TOPICS', 'ID']) eq 'VAR') {
				$topic{ID} = &convertOutput($topicid);
			}
			# トピックタイトル
			if ($tmpl->query(name => ['TOPICS', 'TITLE']) eq 'VAR') {
				$topic{TITLE} = &convertOutput($title);
			}
			# トピック登録時間
			if ($tmpl->query(name => ['TOPICS', 'REGISTTIME']) eq 'VAR') {
				$topic{REGISTTIME} = $registtime;
			}
			# トピック登録者
			if ($tmpl->query(name => ['TOPICS', 'REGISTUSERNAME']) eq 'VAR') {
				$topic{REGISTUSERNAME} = &convertOutput($registusername);
			}
			# トピック登録者URL
			if ($tmpl->query(name => ['TOPICS', 'REGISTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$registuserid;
				# セッション
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$topic{REGISTUSERURL} = &convertOutput($url);
			}
			# トピック最終コメント時間
			if ($tmpl->query(name => ['TOPICS', 'LASTTIME']) eq 'VAR') {
				$topic{LASTTIME} = $lasttime;
			}
			# トピック最終コメント者
			if ($tmpl->query(name => ['TOPICS', 'LASTUSERNAME']) eq 'VAR') {
				$topic{LASTUSERNAME} = &convertOutput($lastusername);
			}
			# トピック最終コメントURL
			if ($tmpl->query(name => ['TOPICS', 'LASTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$lastuserid;
				# セッション
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$topic{LASTUSERURL} = &convertOutput($url);
			}
			# トピックコメント数
			if ($tmpl->query(name => ['TOPICS', 'COMMENTCOUNT']) eq 'VAR') {
				$topic{COMMENTCOUNT} = $commentcount;
			}
			push(@topicvars, \%topic);
		}
		$tmpl->param(TOPICS => \@topicvars);
	}

	# 前ページ
	if ($start > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $prevstart = $start - $size;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		my $url = &getCondUrl();
		$url .= '&start='.$prevstart;
		$url .= '&size='.$size;
		$tmpl->param(PREVPAGEURL => &convertOutput($url));
	}

	# 前ページ番号
	if ($start > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		# 9 ページ以上は移動できない
		my $startno = $no - 9;
		if ($startno < 1) {
			$startno = 1;
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = &getCondUrl();
			# 開始行
			$url .= '&start='.($i-1) * $size;
			$url .= '&size='.$size;
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGEURL']) eq 'VAR') {
				$page{BACKPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGELABEL']) eq 'VAR') {
				$page{BACKPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
		}
		$tmpl->param(BACKPAGELOOP => \@pagedata);
	}

	# 次ページ
	if (($start + @topics) < $topiccount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = &getCondUrl();
		$url .= '&start='.$nextstart;
		$url .= '&size='.$size;
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# 次ページ番号
	if (($start + @topics) < $topiccount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($topiccount / $size);
		if ($topiccount % $size) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = &getCondUrl();
			# 開始行
			$url .= '&start='.($i-1) * $size;
			$url .= '&size='.$size;
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 9 ページ以上は移動できない
			if (@pagedata >= 9) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# 現在ページ
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		# ページ処理する場合だけ表示
		if ($size < $topiccount) {
			my $no = int($start / $size) + 1;
			$tmpl->param(NOWPAGENOLABEL => $no);
		}
	}


	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###########################
# 検索条件を URL エンコード
sub getCondUrl {
	my $url = $cgi->url(-relative=>1).'?';
	$url .= 'forumid='.$forumid;
	# セッション
	if (&isMobile) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id;
	}
	return $url;
}

###########################
# トピック一覧取得
sub getTopicList() {

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 10;
	}

	# トピックIDが指定されていたら表示を開始する行を探す
	if ($cgi->param('topicid')) {
		my $sql = 
			'SELECT a.forumid , count(a.forumid)'.
			' FROM'.
			' topics a, topics b'.
			' WHERE'.
			' a.forumid=b.forumid'.
			' AND a.deleteflag=?'.
			' AND b.deleteflag=?'.
			' AND b.topicid=?'.
			' AND a.lasttime >= b.lasttime'.
			' GROUP BY a.forumid';
		my @bind = ('0', '0', $cgi->param('topicid'));
		my ($fid, $tcount) = &selectFetchArray($dbh, $sql, @bind);
		if ($fid) {
			$forumid = $fid;
			$start = int(($tcount - 1) / $size) * $size;
		} else {
			return 0;
		}
	} else {
		$forumid = $cgi->param('forumid');
		$start = $cgi->param('start') + 0;
	}
	

	$topiccount = 0;
	@topics = ();
	my $sqlcount = 'SELECT count(*)';
	my $sql = 'SELECT a.topicid, a.title, a.registtime, a.lasttime, a.registuserid, b.name, a.lastuserid, c.name, a.commentcount';
	my $sqlwhere = ' FROM topics a, users b, users c, forums d'.
		' WHERE a.registuserid=b.userid AND a.lastuserid=c.userid AND a.forumid=d.forumid AND a.deleteflag=? AND a.forumid=? AND d.deleteflag=? AND d.powerlevel<=?';
	$sqlcount .= $sqlwhere;
	$sql .= $sqlwhere.' ORDER BY a.lasttime DESC';
	my @bind = ('0', $forumid, '0', $session->param('powerlevel'));
	$topiccount = &selectFetch($dbh, $sqlcount, @bind);
	if ($topiccount >= $size) {
		$sql .= ' LIMIT '.$start.', '.$size;
	}
	@topics = &selectFetchArrayRef($dbh, $sql, @bind);
}
