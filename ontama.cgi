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

		# ゴハンを食べる
		my $check = 0;
		if ($cgi->param('food')) {
			$check = &eatFood();
		}

		if (!$check) {
			# 現在の画面
			$msg .= &checkOnline($dbh, $session->param('userid'), 'おんたま');

			# 画面表示
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

	# メッセージ
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();

	# USERID
	my $userid = $cgi->param('userid') || $session->param('userid');


	# おんたま情報取得
	my %ontama = &getOntama($dbh, $userid);
	if ($ontama{'image'}) {
		if ($ontama{'health'}) {
			# 画像 URL
			if ($ontama{'image'} && $tmpl->query(name => 'URL_ONTAMAIMAGE') eq 'VAR') {
				my $url = $config{'ontamaimagesurl'}.'/'.$ontama{'image'};
				$tmpl->param(URL_ONTAMAIMAGE => &convertOutput($url));
			}
		} else {
			# 死亡フラグ
			if ($tmpl->query(name => 'ONTAMADEAD') eq 'VAR') {
				$tmpl->param(ONTAMADEAD => 1);
			}
		}
		
		# おんたまの名前
		if ($ontama{'name'} && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
			$tmpl->param(ONTAMANAME => &convertOutput($ontama{'name'}));
		}

		# 飼い主の名前
		if ($ontama{'ownername'} && $tmpl->query(name => 'OWNERNAME') eq 'VAR') {
			$tmpl->param(OWNERNAME => &convertOutput($ontama{'ownername'}));
		}

		# USERID
		if ($userid != $session->param('userid') && $tmpl->query(name => 'USERID') eq 'VAR') {
			$tmpl->param(USERID => &convertOutput($userid));
		}
		
		# ゴハンをあげる URL
		if ($tmpl->query(name => 'URL_ONTAMAFOOD') eq 'VAR') {
			my $url = 'ontama.cgi?food=1';
			if ($userid != $session->param('userid')) {
				$url .= '&userid='.$userid;
			}
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_ONTAMAFOOD => &convertOutput($url));
		}

		# ゲームをする URL
		if ($tmpl->query(name => 'URL_ONTAMAGAME') eq 'VAR') {
			my $url = 'ontamagame.cgi';
			if ($userid != $session->param('userid')) {
				$url .= '?userid='.$userid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
			} elsif (&isMobile) {
				$url .= '?'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_ONTAMAGAME => &convertOutput($url));
		}

		# おんたまをやめる URL
		if ($userid == $session->param('userid') && $tmpl->query(name => 'URL_DELETEONTAMA') eq 'VAR') {
			my $url = 'deleteontamaconfirm.cgi';
			if (&isMobile) {
					$url .= '?'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_DELETEONTAMA => &convertOutput($url));
		}
		
		# 状態
		if ($tmpl->query(name => 'ONTAMASTATUS') eq 'LOOP') {
			my @status = &getOntamaStatus($dbh, $userid, %ontama);
			my @statusvars = ();
			foreach my $line(@status) {
				my %statusvar;
				# 状態
				if ($tmpl->query(name => ['ONTAMASTATUS', 'VALUE']) eq 'VAR') {
					$statusvar{'VALUE'} = &convertOutput($line);
				}
				push(@statusvars, \%statusvar);
			}
			$tmpl->param(ONTAMASTATUS => \@statusvars);
		}

		# 日記
		if ($tmpl->query(name => 'ONTAMALOGS') eq 'LOOP') {
			my @ontamalogs = &selectFetchArrayRef($dbh, 'SELECT body, registtime FROM ontamalogs WHERE userid=? ORDER BY registtime DESC LIMIT 0, 5', $userid);
			my @vars = ();
			foreach my $row(@ontamalogs) {
				my ($body, $registtime) = @$row;
				my %var;
				# 日付
				if ($tmpl->query(name => ['ONTAMALOGS', 'DATE']) eq 'VAR') {
					if ($registtime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
						$var{'DATE'} = &convertOutput($2.'月'.$3.'日');
					}
				}
				# 本文
				if ($tmpl->query(name => ['ONTAMALOGS', 'VALUE']) eq 'VAR') {
					$var{'VALUE'} = &convertOutput($body, 1);
				}
				push(@vars, \%var);
			}
			$tmpl->param(ONTAMALOGS => \@vars);
		}
	} else {
		$msg .= 'おんたまはいません。';
	}

	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}
	
	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}


################
# ゴハンをあげる
sub eatFood() {
	my $userid = $cgi->param('userid') || $session->param('userid');
	
	my ($lastfood) = &selectFetch($dbh, 'SELECT food FROM ontamausers WHERE userid=?', ($userid));

	if ($lastfood >= 10) {
		$msg .= 'ゴハンは10個以上あげられません。';
		return 0;
	} else {
		$msg .= 'ゴハンをあげました。';
		$session->param('msg', $msg);
		$session->flush();
	}

	my $food = $cgi->param('food');
	if ($food > 10) {
		$food = 10;
	}
	if ($food < 0) {
		$food = 0;
	}
	if ($food) {
		my $sql = 
			'UPDATE ontamausers SET'.
			' food=food+?,'.
			' lasttime=NOW()'.
			' where'.
			' userid=?';
		&doDB($dbh, $sql, ($food, $userid));
	}

	# 画面リダイレクト
	if (&isMobile()) {
		my $url = 'ontama.cgi?'.$config{'sessionname'}.'='.$sid;
		if ($userid != $session->param('userid')) {
			$url .= '&userid='.$userid;
		}
		print $cgi->redirect($url);
	} else {
		my $url = 'ontama.cgi';
		if ($userid != $session->param('userid')) {
			$url .= '?userid='.$userid;
		}
		print $cgi->redirect($url);
	}

	return 1;
}
