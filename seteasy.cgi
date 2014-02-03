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
my @ages = ();

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
	$session = &readSession(1);
	if (defined $session) {
		# �Z�b�V���� ID
		$sid = $session->id;

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �o�^
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &regUser();
		} elsif ($cgi->param('delete')) {
			$check = &delUser();
		}

		# ��ʕ\��
		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '���񂽂񃍃O�C���ݒ�');

			&disp;
		}

		# DB �N���[�Y
		&disconnectDB($dbh);
	}
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###############
# �@����o�^
sub regUser() {
	my $key = &getPhoneID();
	if (!$key) {
		$msg .= '�@�킪���ʂł��܂���ł����B';
		return 0;
	}

	# DB �o�^
	my @bind = ($key, $session->param('userid'));
	my $sql = 
		'UPDATE users SET '.
		'mobcode=? '.
		'where userid=?';
	&doDB($dbh, $sql, @bind);

	$msg .= '�@�����o�^���܂����B';
	$session->param('msg', $msg);
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("alert.cgi?$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('alert.cgi');
	}

	return 1;
}

###############
# �@����폜
sub delUser() {
	# DB �o�^
	my @bind = ('', $session->param('userid'));
	my $sql = 
		'UPDATE users SET '.
		'mobcode=? '.
		'where userid=?';
	&doDB($dbh, $sql, @bind);

	$msg .= '�@������폜���܂����B';
	$session->param('msg', $msg);
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("alert.cgi?$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('alert.cgi');
	}

	return 1;
}

