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

	# �Z�b�V�����ǂݍ���
	$sid = $cgi->cookie($config{'sessionname'}) || $cgi->param($config{'sessionname'}) || undef;
	$session = &readSession;

	# DB �I�[�v��
	$dbh = &connectDB(1);

	my $userid = 0;
	if (defined $session) {
		$userid = $session->param('userid') + 0;
		# ���݂̉��
		$msg .= &checkOnline($dbh, $userid, '���O�A�E�g');
		&logout;
		$msg .= '���O�A�E�g���܂����B';
	} elsif ($sid) {
		# ���݂̉��
		$msg .= &checkOnline($dbh, $userid, '���O�A�E�g');
		$msg .= '�ڑ����^�C���A�E�g���܂����B���O�C�������蒼���Ă��������B';
	} else {
		# ���݂̉��
		$msg .= &checkOnline($dbh, $userid, '���O�A�E�g');
		$msg .= '���O�C�����Ă��܂���B';
	}


	# ��ʕ\��
	&disp;

	# DB �N���[�Y
	&disconnectDB($dbh);
}


##########
# ��ʕ\��
sub disp
{
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	# ���[�U�[
	if ($tmpl->query(name => 'USER') eq 'VAR') {
		$tmpl->param(USER => $cgi->param('user'));
	}

	# �p�X���[�h
	if ($tmpl->query(name => 'PASS') eq 'VAR') {
		$tmpl->param(PASS => $cgi->param('pass'));
	}

	# �ȒP���O�C���t���O
	if ($cgi->param('easylogin') && $tmpl->query(name => 'EASY') eq 'VAR') {
		$tmpl->param(EASY => $cgi->param('easylogin'));
	}

	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

#############
# ���O�A�E�g
sub logout {
	my $sql = 
		'UPDATE onlineusers SET deleteflag=? WHERE userid=?';
	&doDB($dbh, $sql, ('1', $session->param('userid') + 0));

	$session->close;
	$session->delete;
	$session = undef;
}
