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
my $messagecount = 0;
my @messages = ();

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

		# 一覧取得
		&getList();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), '送信済みメッセージ一覧');

		# 画面表示
		&disp();

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
	
	# メッセージ一覧
	if (@messages && $tmpl->query(name => 'MESSAGES') eq 'LOOP') {
		my @messagedata = ();
		foreach my $row(@messages) {
			my ($messageid, $subject, $receiverid, $receivername, $time) = @$row;
			my %message;
			if ($tmpl->query(name => ['MESSAGES', 'URL']) eq 'VAR') {
				my $url = 'sendmessageview.cgi?messageid='.$messageid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$message{'URL'} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['MESSAGES', 'SUBJECT']) eq 'VAR') {
				$message{'SUBJECT'} = &convertOutput($subject);
			}
			if ($tmpl->query(name => ['MESSAGES', 'RECEIVER']) eq 'VAR') {
				$message{'RECEIVER'} = &convertOutput($receivername);
			}
			if ($tmpl->query(name => ['MESSAGES', 'RECEIVERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$receiverid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$message{'RECEIVERURL'} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['MESSAGES', 'TIME']) eq 'VAR') {
				$message{'TIME'} = &convertOutput($time);
			}
			push(@messagedata, \%message);
		}
		$tmpl->param(MESSAGES => \@messagedata);
	}

	# 前ページ
	if ($cgi->param('start') > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $url = $cgi->url(-relative=>1).'?';
		$url .= 'submit=1';
		# 開始行
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $prevstart = $cgi->param('start') - $pagesize;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		$url .= '&start='.$prevstart;
		$url .= '&size='.$pagesize;
		$url .= &getCondUrl();
		$tmpl->param(PREVPAGEURL => &convertOutput($url));
	}

	# 前ページ番号
	if ($cgi->param('start') > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $start = $cgi->param('start') + 0;
		my $no = int($start / $pagesize) + 1;
		my $startno = 1;
		if ($no > 10) {
			$startno = $no - 10
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1).'?';
			$url .= 'submit=1';
			# 開始行
			$url .= '&start='.($i-1) * $pagesize;
			$url .= '&size='.$pagesize;
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
	if (($cgi->param('start') + @messages) < $messagecount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $url = $cgi->url(-relative=>1).'?';
		$url .= 'submit=1';
		# 開始行
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $nextstart = $cgi->param('start') + $pagesize;
		$url .= '&start='.$nextstart;
		$url .= '&size='.$pagesize;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# 次ページ番号
	if (($cgi->param('start') + @messages) < $messagecount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $start = $cgi->param('start') + 0;
		my $no = int($start / $pagesize) + 1;
		my $maxno = int($messagecount / $pagesize);
		if ($messagecount % $pagesize) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1).'?';
			$url .= 'submit=1';
			# 開始行
			$url .= '&start='.($i-1) * $pagesize;
			$url .= '&size='.$pagesize;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 10 ページ以上は移動できない
			if (@pagedata >= 10) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# 現在ページ
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		# ページ処理する場合だけ表示
		if ($pagesize < $messagecount) {
			my $start = $cgi->param('start') + 0;
			my $no = int($start / $pagesize) + 1;
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

###########
# 一覧取得
sub getList() {
	if ($msg) {
		return 0;
	}

	# 検索実行
	my $pagesize = $cgi->param('size') + 0;
	if (!$pagesize) {
		$pagesize = 10; # デフォルトサイズ
	}
	my $pagestart = $cgi->param('start') + 0;
	my @bind = ($session->param('userid'), '0');
	my $sqlcount = 'SELECT count(*) FROM messages a, users b';
	my $sql = 'SELECT a.messageid, a.subject, b.userid, b.name, a.sendtime FROM messages a, users b';
	my $sqlwhere = ' WHERE a.receiver_userid=b.userid AND a.sender_userid=? AND a.sender_deleteflag=? ';
	$sqlcount .= $sqlwhere;
	$sql .= $sqlwhere.' ORDER BY sendtime DESC';

	@messages = ();
	$messagecount = &selectFetch($dbh, $sqlcount, @bind);
	if ($messagecount >= $pagesize) {
		$sql .= ' LIMIT '.$pagestart.', '.$pagesize;
	}
	@messages = &selectFetchArrayRef($dbh, $sql, @bind);

	return 1;
}
