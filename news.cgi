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
my $newscount = 0;
my @news = ();
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

		# 新着一覧取得
		&getNewsList();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'フォーラムの最新の書き込み');

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
	
	# 新着一覧
	if (@news && $tmpl->query(name => 'MORENEWS') eq 'LOOP') {
		my @newsvars = ();
		foreach my $row(@news) {
			my ($forumid, $forumname, $topicid, $title, $lastcommentid, $lastuserid, $lastusername, $lasttime, $commentcount) = @$row;
			my %newsvar = ();
			# 時間
			if ($tmpl->query(name => ['MORENEWS', 'TIME']) eq 'VAR') {
				$newsvar{'TIME'} = &convertOutput($lasttime);
			}
			# 日付
			if ($tmpl->query(name => ['MORENEWS', 'DATE']) eq 'VAR') {
				if ($lasttime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$newsvar{'DATE'} = &convertOutput($2.'月'.$3.'日');
				}
			}
			# トピックタイトル
			if ($tmpl->query(name => ['MORENEWS', 'TOPICTITLE']) eq 'VAR') {
				$newsvar{'TOPICTITLE'} = &convertOutput($title);
			}
			# トピックURL
			if ($tmpl->query(name => ['MORENEWS', 'URL']) eq 'VAR') {
				my $url = 'topic.cgi?';
				if ($lastcommentid) {
					$url .= 'topiccommentid='.$lastcommentid;
				} else {
					$url .= 'topicid='.$topicid;
				}
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				if ($lastcommentid) {
					$url .= '#'.$lastcommentid;
				}
				$newsvar{'URL'} = &convertOutput($url);
			}
			# トピックコメント数
			if ($tmpl->query(name => ['MORENEWS', 'COUNT']) eq 'VAR') {
				$newsvar{'COUNT'} = &convertOutput($commentcount);
			}
			# フォーラム名
			if ($tmpl->query(name => ['MORENEWS', 'FORUMNAME']) eq 'VAR') {
				$newsvar{'FORUMNAME'} = &convertOutput($forumname);
			}
			# フォーラムURL
			if ($tmpl->query(name => ['MORENEWS', 'FORUMURL']) eq 'VAR') {
				my $url = 'forum.cgi?topicid='.$topicid;
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				$url .= '#'.$topicid;
				$newsvar{'FORUMURL'} = &convertOutput($url);
			}
			# 最終投稿者
			if ($tmpl->query(name => ['MORENEWS', 'LASTUSERNAME']) eq 'VAR') {
				$newsvar{'LASTUSERNAME'} = &convertOutput($lastusername);
			}
			# 最終投稿者URL
			if ($tmpl->query(name => ['MORENEWS', 'LASTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$lastuserid;
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				$newsvar{'LASTUSERURL'} = &convertOutput($url);
			}
			push(@newsvars, \%newsvar);
		}
		$tmpl->param(MORENEWS=> \@newsvars);
	}

	# 前ページ
	if ($start > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $prevstart = $start - $size;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$prevstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
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
			my $url = $cgi->url(-relative=>1);
			$url .= '?start='.($i-1) * $size;
			$url .= '&size='.$size;
			$url .= &getCondUrl();
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
	if (($start + @news) < $newscount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$nextstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# 次ページ番号
	if (($start + @news) < $newscount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($newscount / $size);
		if ($newscount % $size) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1);
			$url .= '?start='.($i-1) * $size;
			$url .= '&size='.$size;
			$url .= &getCondUrl();
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
		if ($size < $newscount) {
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
	my $url = '';
	# セッション
	if (&isMobile()) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id();
	}
	return $url;
}


#####################
# 新着一覧取得
sub getNewsList() {
	$newscount = 0;
	@news = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 10;
	}

	# 件数取得
	my $sql = 
			'SELECT'.
			' count(*)'.
			' FROM'.
			' topics a,'.
			' users c,'.
			' forums d'.
			' WHERE'.
			' a.lastuserid=c.userid AND'.
			' a.forumid=d.forumid AND'.
			' a.deleteflag=? AND'.
			' d.deleteflag=? AND'.
			' d.powerlevel<=?';
	my @bind = ('0', '0', $session->param('powerlevel'));
	$newscount = &selectFetch($dbh, $sql, @bind);

	# データがある
	if ($newscount) {
		if ($cgi->param('start')) {
			$start = $cgi->param('start') + 0;
		}

		my $sql = 
			'SELECT'.
			' a.forumid,'.
			' d.name,'.
			' a.topicid,'.
			' a.title,'.
			' a.lastcommentid,'.
			' a.lastuserid,'.
			' c.name,'.
			' a.lasttime,'.
			' a.commentcount'.
			' FROM'.
			' topics a,'.
			' users c,'.
			' forums d'.
			' WHERE'.
			' a.lastuserid=c.userid AND'.
			' a.forumid=d.forumid AND'.
			' a.deleteflag=? AND'.
			' d.deleteflag=? AND'.
			' d.powerlevel<=?'.
			' ORDER BY a.lasttime DESC';
		if ($newscount >= $size) {
			$sql .= ' LIMIT '.$start.', '.$size;
		}
		my @bind = ('0', '0', $session->param('powerlevel'));
		@news = &selectFetchArrayRef($dbh, $sql, @bind);
	}
}
