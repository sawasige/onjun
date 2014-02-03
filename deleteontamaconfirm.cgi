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
my @ages = ();

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
				print $cgi->redirect("ontama.cgi?$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("ontama.cgi");
			}
		} else {
			# DB オープン
			$dbh = &connectDB(1);

			# 登録
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &registValue();
			}
			
			# DB クローズ
			&disconnectDB($dbh);

			# 画面表示
			if (!$check) {
				# 現在の画面
				$msg .= &checkOnline($dbh, $session->param('userid'), 'おんたま消去確認');

				&disp;
			}
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
			if ($tmpl->query(name => 'ONTAMADEAD') eq 'VAR') {
				$tmpl->param(ONTAMADEAD => 1);
			}
		}
		
		# おんたまの名前
		if ($ontama{'name'} && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
			$tmpl->param(ONTAMANAME => &convertOutput($ontama{'name'}));
		}

		# 飼い主の名前
		if ($ontama{'ownername'} && $tmpl->query(name => 'ONTAMAOWNERNAME') eq 'VAR') {
			$tmpl->param(ONTAMAOWNERNAME => &convertOutput($ontama{'ownername'}));
		}

		# USERID
		if ($userid != $session->param('userid') && $tmpl->query(name => 'USERID') eq 'VAR') {
			$tmpl->param(USERID => &convertOutput($userid));
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

#################
# メッセージ送信
sub registValue() {
	my $userid = $cgi->param('userid') || $session->param('userid');

	if ($session->param('powerlevel') < 5 && $userid != $session->param('userid')) {
		$msg .= '他人のおんたまは消去できません。';
		return 0;
	}

	# データチェック
	if (!$userid) {
		$msg .= 'パラメータが不正です。';
		return 0;
	}

	my $sql = 'SELECT image FROM ontamausers WHERE userid=?';
	my $image = &selectFetch($dbh, $sql, ($userid));

	# 画像ファイル削除
	unlink($config{'ontamaimagesdir'}.'/'.$image);
	
	# DB 登録
	&doDB($dbh, 'DELETE FROM ontamausers WHERE userid=?', $userid);
	&doDB($dbh, 'DELETE FROM ontamastatus WHERE userid=?', $userid);
	&doDB($dbh, 'DELETE FROM ontamalogs WHERE userid=?', $userid);

	$msg .= 'おんたまを消去しました。';
	$session->param('msg', $msg);
	$session->flush();

	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("alert.cgi?$config{'sessionname'}=$sid");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('alert.cgi');
	}

	return 1;
}

