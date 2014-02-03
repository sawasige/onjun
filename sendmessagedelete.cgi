#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
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
my %message = ();

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
		
		# �L�����Z���Ȃ�߂�
		if ($cgi->param('cancel')) {
			# ��ʃ��_�C���N�g
			my $url = 'sendmessageview.cgi?messageid='.$cgi->param('messageid');
			if (&isMobile()) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			print $cgi->redirect($url);
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �폜
			my $check = 0;
			if ($cgi->param('submit')) {
				$check =&deleteMessage();
			}

			if (!$check) {
				# ���b�Z�[�W�擾
				&getMessage();

				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '���M�ς݃��b�Z�[�W�폜');

				# ��ʕ\��
				&disp;
			}

			# DB �N���[�Y
			&disconnectDB($dbh);
		}
	}
	
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	if ($message{'subject'}) {
		# ����
		if ($tmpl->query(name => 'RECEIVER_NAME') eq 'VAR') {
			$tmpl->param(RECEIVER_NAME => &convertOutput($message{'receiver_name'}));
		}
		# ���M����
		if ($tmpl->query(name => 'SENDTIME') eq 'VAR') {
			$tmpl->param(SENDTIME => &convertOutput($message{'sendtime'}));
		}
		# �T�u�W�F�N�g
		if ($tmpl->query(name => 'SUBJECT') eq 'VAR') {
			$tmpl->param(SUBJECT => &convertOutput($message{'subject'}));
		}
		# �{��
		if ($tmpl->query(name => 'BODY') eq 'VAR') {
			$tmpl->param(BODY => &convertOutput($message{'body'}, 1));
		}
		# ���b�Z�[�W�ԍ�
		if ($tmpl->query(name => 'MESSAGEID') eq 'VAR') {
			$tmpl->param(MESSAGEID => $cgi->param('messageid'));
		}

	} else {
		$msg .= '���b�Z�[�W������܂���B';
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

#################
# ���b�Z�[�W�擾
sub getMessage() {
	my $messageid = $cgi->param('messageid');
	if ($messageid) {
		my $sql = 'SELECT a.subject, a.body, a.sendtime, b.name FROM messages a, users b'.
			' WHERE a.receiver_userid=b.userid AND a.messageid=? AND a.sender_userid=? AND a.sender_deleteflag=?';
		my @bind = ($messageid, $session->param('userid'), 0);
		my ($subject, $body, $sendtime, $receiver_name) = &selectFetchArray($dbh, $sql, @bind);
		if ($subject) {
			$message{'subject'} = $subject;
			$message{'body'} = $body;
			$message{'receiver_name'} = $receiver_name;
			$message{'sendtime'} = $sendtime;
		}
	}
}

#################
# ���b�Z�[�W�폜
sub deleteMessage() {
	my $messageid = $cgi->param('messageid');
	if (!$messageid) {
		return 0;
	}
	my @bind = ('1', $messageid, $session->param('userid'));
	my $sql = 'UPDATE messages SET sender_deleteflag=? WHERE messageid=? AND sender_userid=?';
	&doDB($dbh, $sql, @bind);

	$msg .= '���M�ς݃��b�Z�[�W���폜���܂����B';

	$session->param('msg', $msg);
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("sendmessagelist.cgi?$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('sendmessagelist.cgi');
	}

	return 1;
}

