#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;
use CGI::Session;
use HTML::Template;
use File::Copy;
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
				print $cgi->redirect("setontama.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# セッションは Cookie 埋め込まれている
				print $cgi->redirect("setontama.cgi?cancel=1");
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
				$msg .= &checkOnline($dbh, $session->param('userid'), 'おんたま開始確認');

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

	if (!$msg) {
		my $ontamaname = $session->param('ontamaname');

		if ($ontamaname && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
			$tmpl->param(ONTAMANAME => &convertOutput($ontamaname));
		}
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
	my $ontamaname = $session->param('ontamaname');

	# データチェック
	if (!$ontamaname) {
		$msg .= 'パラメータが不正です。';
		return 0;
	}

	my $sql = 'SELECT ontamaid, image FROM ontama WHERE parentid=?';
	my @ontamalist = &selectFetchArrayRef($dbh, $sql, (0));
	my $idx = int(rand(@ontamalist + 0));
	my $ontama = $ontamalist[$idx];
	my ($ontamaid, $sourceimage) = @$ontama;

	# 画像ファイル名
	my $destimage = $session->param('userid').'_'.&getRandomString(3).'.gif';

	# 画像ファイルコピー
	copy($config{'ontamadir'}.'/'.$sourceimage, $config{'ontamaimagesdir'}.'/'.$destimage);
	
	# DB 登録
	my @bind = ($session->param('userid'), $ontamaid, $ontamaname, $destimage, 1, 1, 0, 50, 50, 50);
	my $sql =  'INSERT INTO ontamausers(userid, ontamaid, name, image, days, level, grow, health, hungry, happy, growdate, registtime, lasttime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW(), NOW(), NOW())';
	&doDB($dbh, $sql, @bind);

	$msg .= 'おんたまのたまごの用意ができました。成長を楽しみにしていてください！';
	$session->clear(['ontamaname']);
	$session->param('msg', $msg);
	$session->flush();

	
	# 画面リダイレクト
	if (&isMobile()) {
		# セッションは URL 埋め込み
		print $cgi->redirect("ontama.cgi?$config{'sessionname'}=$sid");
	} else {
		# セッションは Cookie 埋め込まれている
		print $cgi->redirect('ontama.cgi');
	}

	return 1;
}

