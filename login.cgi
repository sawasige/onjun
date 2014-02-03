#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
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

#�v���O�����J�n
&main;

##########
# ���C��
sub main {
	$cgi = new CGI;
	$msg = '';

	# �ݒ�ǂݍ���
	%config = &config;

	# �Z�b�V�����擾
	$session = &readSession;
	if (defined $session) {
		$sid = $session->id();
	}

	$dbh = &connectDB(1);

	# ���O�C��
	my $login = 0;
	if ($cgi->param('login') || $cgi->param('easylogin')) {
		$login = &login;
	}
	
	# ��ʕ\��
	if (!$login) {
		&disp;
	}

	&disconnectDB($dbh);
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	if ($session) {
		$msg .= $session->param('msg');
		$session->clear(['msg']);
		$session->flush();
	}

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);
	
	# ���b�Z�[�W�i����΁j
	my $phone = &getPhone();
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	if (&isMobile) {
		print $cgi->header(-charset=>'Shift_JIS');
	} else {
		print $cgi->header(
			-charset=>'Shift_JIS',
			-cookie=>$cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id));
	}
	print $tmpl->output;
}


###########
# ���O�C��
sub login {
	my $login = 0;
	my ($userid, $name, $powerlevel);
	if ($cgi->param('login')) {
		if (!$cgi->param('user')) {
			$msg .= '���[�U�[�����w�肵�Ă��������B';
		} elsif (!$cgi->param('pass')) {
			$msg .= '�p�X���[�h���w�肵�Ă��������B';
		} else {
			my @bind = ($cgi->param('user'), $cgi->param('pass'), '0');
			my @users = &selectFetchArray($dbh, 'SELECT userid, name, powerlevel FROM users WHERE name=? AND pass=? AND deleteflag=?', @bind);
			if (@users) {
				$userid = $users[0];
				$name = $users[1];
				$powerlevel = $users[2];
				$login = 1;
			} else {
				$msg .= '���[�U�[���A�܂��̓p�X���[�h���Ⴂ�܂��B';
			}
		}
	} elsif ($cgi->param('easylogin')) {
		# �g�є���
		my $key = &getPhoneID();

		if ($key){
			my @bind = ($key, '0');
			my @users = &selectFetchArray($dbh, 'SELECT userid, name, powerlevel FROM users WHERE mobcode=? AND deleteflag=?', @bind);
			if (@users) {
				$userid = $users[0];
				$name = $users[1];
				$powerlevel = $users[2];
				$login = 1;
			} else {
				$msg .= '���g���̋@��͖��o�^�ł��B�ʏ�ʂ胍�O�C�����Ă��������B';
			}
		} else {
			$msg .= '�@�킪���ʂł��܂���ł����B';
		}
	} else {
		die;
	}
	
	# ���O�C����������
	if ($login) {
		&writeLog(3, $name.'���O�C��');

		$session->param('userid', $userid);
		$session->param('powerlevel', $powerlevel);
		$session->param('info', $name.'����悤������');
		$session->flush();
		# ���O�C�����ԋL�^
		&doDB($dbh, 'UPDATE users SET useragent=?, lasttime=now() WHERE userid=?', ($ENV{'HTTP_USER_AGENT'}, $userid));

		my $url = '';
		if ($session->param('openurl')) {
			$url = $session->param('openurl');
			$session->clear(['openurl']);
			$session->flush();
		} else {
			$url = 'home.cgi'
		}

		# ��ʃ��_�C���N�g
		if (&isMobile()) {
			if ($url =~ /\?/) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id();
			} else {
				$url .= '?'.$config{'sessionname'}.'='.$session->id();
			}
			print $cgi->redirect($url);
		} elsif ($cgi->param('saveuser')) {
			my $cookie1 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id);
			my $cookie2 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>'user', -value=>$name, -expires=>'+1y');
			print $cgi->redirect(
				-uri=>$url,
				-cookie=>[$cookie1, $cookie2]);
		} else {
			my $cookie1 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id);
			my $cookie2 = $cgi->cookie(-path=>$config{'cookie_path'}, -name=>'user', -value=>'', -expires=>'-1d');
			print $cgi->redirect(
				-uri=>$url,
				-cookie=>[$cookie1, $cookie2]);
		}
	}
	
	return $login;
}

