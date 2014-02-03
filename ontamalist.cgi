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
my $listcount = 0;
my @list = ();
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

		# 一覧取得
		&getList();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'おんたま一覧');

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
	
	# 一覧
	if (@list && $tmpl->query(name => 'ONTAMALIST') eq 'LOOP') {
		my @vars = ();
		foreach my $row(@list) {
			my ($userid, $name, $image, $days, $health, $ownername) = @$row;
			my %var = ();
			if ($health) {
				# 画像 URL
				if ($tmpl->query(name =>  ['ONTAMALIST', 'URL_ONTAMAIMAGE']) eq 'VAR') {
					my $url = $config{'ontamaimagesurl'}.'/'.$image;
					$var{'URL_ONTAMAIMAGE'} =  &convertOutput($url);
				}
			} else {
				# 死亡フラグ
				if ($tmpl->query(name =>  ['ONTAMALIST', 'DEAD']) eq 'VAR') {
					$var{'DEAD'} = 1;
				}
			}
			# 名前
			if ($tmpl->query(name => ['ONTAMALIST', 'NAME']) eq 'VAR') {
				$var{'NAME'} = &convertOutput($name);
			}
			# 飼い主
			if ($tmpl->query(name => ['ONTAMALIST', 'OWNERNAME']) eq 'VAR') {
				$var{'OWNERNAME'} = &convertOutput($ownername);
			}
			# 日数
			if ($tmpl->query(name => ['ONTAMALIST', 'DAYS']) eq 'VAR') {
				$var{'DAYS'} = &convertOutput($days);
			}
			# おんたまURL
			if ($tmpl->query(name => ['ONTAMALIST', 'ONTAMAURL']) eq 'VAR') {
				my $url = 'ontama.cgi?userid='.$userid;
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				$var{'ONTAMAURL'} = &convertOutput($url);
			}
			push(@vars, \%var);
		}
		$tmpl->param(ONTAMALIST=> \@vars);
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
	if (($start + @list) < $listcount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$nextstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# 次ページ番号
	if (($start + @list) < $listcount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($listcount / $size);
		if ($listcount % $size) {
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
		if ($size < $listcount) {
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


############
# 一覧取得
sub getList() {
	$listcount = 0;
	@list = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 10;
	}

	# 件数取得
	my $sql = 
		'SELECT'.
		' COUNT(*)'.
		' FROM'.
		' ontamausers a,'.
		' users b'.
		' WHERE'.
		' a.userid=b.userid AND'.
		' b.deleteflag=?';
	my @bind = ('0');
	$listcount = &selectFetch($dbh, $sql, @bind);

	# データがある
	if ($listcount) {
		if ($cgi->param('start')) {
			$start = $cgi->param('start') + 0;
		}

		my $sql = 
			'SELECT'.
			' a.userid,'.
			' a.name,'.
			' a.image,'.
			' a.days,'.
			' a.health,'.
			' b.name'.
			' FROM'.
			' ontamausers a,'.
			' users b'.
			' WHERE'.
			' a.userid=b.userid AND'.
			' b.deleteflag=?'.
			' ORDER BY a.level DESC, a.grow DESC';
		if ($listcount >= $size) {
			$sql .= ' LIMIT '.$start.', '.$size;
		}
		my @bind = ('0');
		@list = &selectFetchArrayRef($dbh, $sql, @bind);
	}
}
