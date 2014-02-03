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
			$check = &checkOption();
		}

		# ��ʕ\��
		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '�I�v�V����');

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

	my $mailmessageflag = '1';
	my $check = 1;
	if ($cgi->param('cancel')) {
		# ���b�Z�[�W���m�点���[��
		$mailmessageflag = $session->param('mailmessageflag');
	} elsif ($cgi->param('submit')) {
		# ���b�Z�[�W���m�点���[��
		$mailmessageflag = $cgi->param('mailmessageflag');
	} else {
		# ���b�Z�[�W���m�点���[��
		my @bind = ($session->param('userid'));
		$mailmessageflag = &selectFetch($dbh, 'SELECT mailmessageflag FROM users WHERE userid=?', @bind);
	}
	
	if ($check) {
		if (($mailmessageflag eq '1' || $mailmessageflag eq 'on') && $tmpl->query(name => 'MAILMESSAGEFLAG') eq 'VAR') {
			$tmpl->param(MAILMESSAGEFLAG => 'checked');
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}


###############
# ���̓`�F�b�N
sub checkOption() {
	if ($msg) {
		return 0;
	}

	# ���b�Z�[�W���m�点���[��
	my $mailmessageflag = $cgi->param('mailmessageflag');
	if ($mailmessageflag eq 'on') {
		$mailmessageflag = '1';
	} elsif (!$mailmessageflag) {
		$mailmessageflag = '0';
	} else {
		$msg .= '���b�Z�[�W���m�点���[���̒l���s���ł��B';
		return 0;
	};

	# ���̓`�F�b�N�����I�I
	$session->param('mailmessageflag', $mailmessageflag);
	$session->flush();
	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect('optionconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# �Z�b�V������ Cookie ���ߍ���
		print $cgi->redirect('optionconfirm.cgi');
	}

	return 1;
}

