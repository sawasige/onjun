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
		$msg .= &checkOnline($dbh, $session->param('userid'), 'プロフィール');

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

	my ($user, $realname, $birthday, $sex, $blood, $job, $part, $place, $age, $note, $lasttime, $useragent) = &getUserInfo();
	$birthday =~ s/-//g;
	if ($birthday eq '00000000') {
		$birthday = '';
	}
	
	# ユーザー情報が取得できている
	if ($user) {
	
		# メッセージを送る
		if ($tmpl->query(name => 'URL_SENDMESSAGE') eq 'VAR') {
			if ($cgi->param('userid') && $session->param('userid') != $cgi->param('userid')) {
				my $url = 'sendmessage.cgi?receiver_userid='.$cgi->param('userid');
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(URL_SENDMESSAGE => &convertOutput($url));
			}
		}
		# プロフィール変更の URL
		if ($tmpl->query(name => 'URL_EDITPROFILE') eq 'VAR') {
			if ($session->param('powerlevel') >= 5 || !$cgi->param('userid') || $session->param('userid') == $cgi->param('userid')) {
				my $userid = $cgi->param('userid') || $session->param('userid');
				my $url = 'editprofile.cgi?userid='.$userid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(URL_EDITPROFILE => &convertOutput($url));
			}
		}

		# ユーザー名
		if ($tmpl->query(name => 'USER') eq 'VAR') {
			$tmpl->param(USER => &convertOutput($user));
		}
		# 本名
		if ($tmpl->query(name => 'REALNAME') eq 'VAR') {
			$tmpl->param(REALNAME => &convertOutput($realname));
		}
		# 誕生日
		if ($tmpl->query(name => 'BIRTHDAY') eq 'VAR') {
			if ($birthday =~ /(....)(..)(..)/) {
				my $b = "$1-$2-$3";
				$tmpl->param(BIRTHDAY => &convertOutput($b));
			}
		}
		# 性別
		if ($tmpl->query(name => 'SEX') eq 'VAR') {
			if ($sex eq 'M') {
				$tmpl->param(SEX => '男性');
			} elsif ($sex eq 'F') {
				$tmpl->param(SEX => '女性');
			}
		}
		# 血液型
		if ($tmpl->query(name => 'BLOOD') eq 'VAR') {
			if ($blood eq 'A') {
				$tmpl->param(BLOOD => 'A型');
			} elsif ($blood eq 'B') {
				$tmpl->param(BLOOD => 'B型');
			} elsif ($blood eq 'O') {
				$tmpl->param(BLOOD => 'O型');
			} elsif ($blood eq 'AB') {
				$tmpl->param(BLOOD => 'AB型');
			}
		}
		# 職業
		if ($tmpl->query(name => 'JOB') eq 'VAR') {
			$tmpl->param(JOB => &convertOutput($job));
		}
		# 楽器
		if ($tmpl->query(name => 'PART') eq 'VAR') {
			$tmpl->param(PART => &convertOutput($part));
		}
		# 住所
		if ($tmpl->query(name => 'PLACE') eq 'VAR') {
			$tmpl->param(PLACE => &convertOutput($place));
		}

		# 期
		if ($tmpl->query(name => 'AGE') eq 'VAR') {
			if ($age) {
				my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
				$now_year = $now_year + 1900;
				$now_month++;
				my $year = $age + 1976;
				my $class = $now_year - $year + 3;
				if ($now_month >= 4) {
					$class++;
				}
				if ($class > 3) {
					$tmpl->param(AGE => $age.'期'.$year.'年卒業');
				} else {
					$tmpl->param(AGE => $age.'期'.$class.'年生');
				}
			}
		}

		# 自己紹介
		if ($tmpl->query(name => 'NOTE') eq 'VAR') {
			$tmpl->param(NOTE => &convertOutput($note, 1));
		}

		# 管理者用
		if ($session->param('powerlevel') >= 5) {
			# 最終ログイン時間
			if ($tmpl->query(name => 'LASTTIME') eq 'VAR') {
				$tmpl->param(LASTTIME => &convertOutput($lasttime));
			}

			# 最終ユーザーエージェント
			if ($tmpl->query(name => 'USERAGENT') eq 'VAR') {
				$tmpl->param(USERAGENT => &convertOutput($useragent));
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

########################
# 現在のユーザー情報取得
sub getUserInfo() {
	my $userid = $cgi->param('userid') || $session->param('userid');
	my @bind = ($userid, '0');
	my @users = &selectFetchArray($dbh, 'SELECT name, realname, birthday, sex, blood, job, part, place, age, note, lasttime, useragent FROM users WHERE userid=? and deleteflag=?', @bind);
	if (@users) {
		return @users;
	} else {
		$msg .= 'ユーザー情報が取得できませんでした。';
		return 0;
	}
}


