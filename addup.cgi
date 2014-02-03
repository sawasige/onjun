#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './mail.pl';
require './jcode.pl';

my $cgi;
my %config;
my $msg;
my $session;
my $sid;

my $dbh;
my $usercount = 0;
my @users = ();
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
		# セッション ID
		$sid = $session->id;
		
		# DB オープン
		$dbh = &connectDB(1);

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), '集計');

		# 集計（改ページされてる場合は集計しない）
		if (!$cgi->param('start')) {
			&addup();
		}

		# 集計結果取得
		&getAddup();

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


	# コメント一覧
	if (@users && $tmpl->query(name => 'USERS') eq 'LOOP') {
		my @uservars = ();
		my $userno = $start + 1;
		foreach my $row(@users) {
			my ($userid, $messagecount, $topiccount, $topiccommentcount, $name) = @$row;
			my %commentvar;
			# ユーザー連番
			if ($tmpl->query(name => ['USERS', 'USERNO']) eq 'VAR') {
				$commentvar{'USERNO'} = &convertOutput($userno);
			}
			$userno++;
			# ユーザーID
			if ($tmpl->query(name => ['USERS', 'USERID']) eq 'VAR') {
				$commentvar{'USERID'} = &convertOutput($userid);
			}
			# ユーザー名
			if ($tmpl->query(name => ['USERS', 'USERNAME']) eq 'VAR') {
				$commentvar{'USERNAME'} = &convertOutput($name);
			}
			# ユーザーURL
			if ($tmpl->query(name => ['USERS', 'USERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'USERURL'} = &convertOutput($url);
			}
			# メッセージ数
			if ($tmpl->query(name => ['USERS', 'MESSAGECOUNT']) eq 'VAR') {
				$commentvar{'MESSAGECOUNT'} = &convertOutput($messagecount);
			}
			# トピック数
			if ($tmpl->query(name => ['USERS', 'TOPICCOUNT']) eq 'VAR') {
				$commentvar{'TOPICCOUNT'} = &convertOutput($topiccount);
			}
			# トピックコメント数
			if ($tmpl->query(name => ['USERS', 'TOPICCOMMENTCOUNT']) eq 'VAR') {
				$commentvar{'TOPICCOMMENTCOUNT'} = &convertOutput($topiccommentcount);
			}

			push(@uservars, \%commentvar);
		}
		$tmpl->param(USERS => \@uservars);
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
	if (($start + @users) < $usercount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$nextstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# 次ページ番号
	if (($start + @users) < $usercount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($usercount / $size);
		if ($usercount % $size) {
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
		if ($size < $usercount) {
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
	if (&isMobile) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id;
	}
	return $url;
}

######
# 集計
sub addup {
	# 集計テーブル更新
	my @allusers = &selectFetchArrayRef($dbh, 'SELECT userid FROM users WHERE deleteflag=?', '0');
	foreach my $row(@allusers) {
		my ($userid) = @$row;
		
		my $messagecount = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE sender_userid=?', $userid);
		my $topiccount = &selectFetch($dbh, 'SELECT count(*) FROM topics WHERE registuserid=? AND deleteflag=?', ($userid, '0'));
		my $topiccommentcount = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE registuserid=? AND deleteflag=?', ($userid, '0'));

		if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
			my $sql = 
				'UPDATE addup SET'.
				' messagecount=?,'.
				' topiccount=?,'.
				' topiccommentcount=?'.
				' WHERE'.
				' userid=?';
			my @bind = ($messagecount, $topiccount, $topiccommentcount, $userid);
			&doDB($dbh, $sql, @bind);
		} else {
			my $sql = 
				'INSERT addup ('.
				' userid,'.
				' messagecount,'.
				' topiccount,'.
				' topiccommentcount'.
				') VALUES (?, ?, ?, ?)';
			my @bind = ($userid, $messagecount, $topiccount, $topiccommentcount);
			&doDB($dbh, $sql, @bind);
		}
	}
}
	
##################
# 集計結果取得
sub getAddup {
	$usercount = 0;
	@users = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 20;
	}

	# 件数取得
	$usercount = &selectFetch($dbh, 'SELECT count(*) FROM addup a, users b WHERE a.userid=b.userid AND b.deleteflag=?', '0');

	# データがある
	if ($usercount) {
		if ($cgi->param('start')) {
			$start = $cgi->param('start') + 0;
		}

		my $sql =
			'SELECT'.
			' a.userid,'.
			' a.messagecount,'.
			' a.topiccount,'.
			' a.topiccommentcount,'.
			' b.name'.
			' FROM'.
			' addup a,'.
			' users b'.
			' WHERE'.
			' a.userid=b.userid'.
			' AND b.deleteflag=?'.
			' ORDER BY b.registtime';
		if ($usercount >= $size) {
			$sql .= ' LIMIT '.$start.', '.$size;
		}
		@users = &selectFetchArrayRef($dbh, $sql, '0');
		
	}
}

