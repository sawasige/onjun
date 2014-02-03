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

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'おんたまゲーム');

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

	my $userid = $cgi->param('userid') || $session->param('userid');
	my $gametype = $cgi->param('gametype');


	# おんたま情報取得
	my %ontama = &getOntama($dbh, $userid);
	if ($ontama{'image'} && $ontama{'health'}) {
		# 画像 URL
		if ($ontama{'image'} && $tmpl->query(name => 'URL_ONTAMAIMAGE') eq 'VAR') {
			my $url = $config{'ontamaimagesurl'}.'/'.$ontama{'image'};
			$tmpl->param(URL_ONTAMAIMAGE => &convertOutput($url));
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

		my @gamemassages = ();
		if (!$ontama{'happydiff'}) {
			$msg .= 'まだゲームはできないみたいです。';
		} elsif ($gametype == 0) {
			# じゃんけん
			if ($tmpl->query(name => 'JANKEN') eq 'VAR') {
				$tmpl->param(JANKEN => 1);
				push(@gamemassages, $ontama{'ownername'}.'さんの'.$ontama{'name'}.'とじゃんけん勝負です！');
				push(@gamemassages, '');
				push(@gamemassages, '「じゃ～んけ～ん…」');
			}

			if ($cgi->param('gu') || $cgi->param('choki') || $cgi->param('pa')) {
				@gamemassages = ();
				push(@gamemassages, '「ぽんっ！」');
				push(@gamemassages, '');
				my @hand = ('グー', 'チョキ', 'パー');
				my $userhandindex = 0;
				if ($cgi->param('gu')) {
					$userhandindex = 0;
				} elsif ($cgi->param('choki')) {
					$userhandindex = 1;
				} else {
					$userhandindex = 2;
				}
				my $userhand = $hand[$userhandindex];
				my $ontamahand = '';
				my $idx = int(rand(3));
				if ($idx == 0) {
					# 引き分け
					$ontama{'happy'} = &playGame($userid, $ontama{'happy'}, 1);
					$ontamahand = $userhand;
					push(@gamemassages, 'あなたの手「'.$userhand.'」');
					push(@gamemassages, 'おんたまの手「'.$ontamahand.'」');
					push(@gamemassages, '');
					push(@gamemassages, '引き分けです！');
				} elsif ($idx == 1) {
					# ユーザーの勝ち
					$ontama{'happy'} = &playGame($userid, $ontama{'happy'}, 3);
					my $ontamahandindex = $userhandindex + 1;
					if ($ontamahandindex > 2) {
						$ontamahandindex = 0;
					}
					$ontamahand = $hand[$ontamahandindex];
					push(@gamemassages, 'あなたの手「'.$userhand.'」');
					push(@gamemassages, 'おんたまの手「'.$ontamahand.'」');
					push(@gamemassages, '');
					push(@gamemassages, 'あなたの勝ちです！');
				} else {
					# ユーザーの負け
					my $ontamahandindex = $userhandindex - 1;
					if ($ontamahandindex < 0) {
						$ontamahandindex = 2;
					}
					$ontamahand = $hand[$ontamahandindex];
					push(@gamemassages, 'あなたの手「'.$userhand.'」');
					push(@gamemassages, 'おんたまの手「'.$ontamahand.'」');
					push(@gamemassages, '');
					push(@gamemassages, 'あなたの負けです！');
				}

				if ($tmpl->query(name => 'USERHAND') eq 'VAR') {
					$tmpl->param(USERHAND => &convertOutput($userhand));
				}
				if ($tmpl->query(name => 'ONTAMAHAND') eq 'VAR') {
					$tmpl->param(ONTAMAHAND => &convertOutput($ontamahand));
				}
				if ($tmpl->query(name => 'JANKEN') eq 'VAR') {
					$tmpl->param(JANKEN => 0);
				}
				
				# もういちどの URL
				if ($tmpl->query(name => 'URL_ONTAMAGAMERETRY') eq 'VAR') {
					my $url = 'ontamagame.cgi?gametype='.$gametype;
					if ($userid != $session->param('userid')) {
						$url .= '&userid='.$userid;
					}
					if (&isMobile) {
						$url .= '&'.$config{'sessionname'}.'='.$session->id;
					}
					$tmpl->param(URL_ONTAMAGAMERETRY => &convertOutput($url));
				}
			}

		} else {
			$msg .= 'ゲームタイプが不正です。';
		}

		# ゲームメッセージ
		if ($tmpl->query(name => 'GAMEMASSAGE') eq 'LOOP') {
			my @massagevars = ();
			foreach my $line(@gamemassages) {
				my %massagevar;
				# 状態
				if ($tmpl->query(name => ['GAMEMASSAGE', 'VALUE']) eq 'VAR') {
					$massagevar{'VALUE'} = &convertOutput($line);
				}
				push(@massagevars, \%massagevar);
			}
			$tmpl->param(GAMEMASSAGE => \@massagevars);
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



	} elsif ($ontama{'image'}) {
		$msg .= 'おんたまは死んでます。';
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


#########
# あそぶ
sub playGame($) {
	my ($userid, $happy, $happyadd) = @_;

	$happy += $happyadd * 20;
	if ($happy > 100) {
		$happy = 100;
	} elsif ($happy < 0) {
		$happy = 0;
	}

	my $sql = 
		'UPDATE ontamausers SET'.
		' happy=?,'.
		' lasttime=NOW()'.
		' where'.
		' userid=?';
	&doDB($dbh, $sql, ($happy, $userid));
	
	return $happy;
}
