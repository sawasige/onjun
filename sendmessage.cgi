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
			$check = &checkMessage();
		}

		# ��ʕ\��
		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '���b�Z�[�W���M');

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

	my $replyid = 0;
	my $reply_name = '';
	my $reply_subject = '';
	my $reply_body = '';
	my $receiver_userid = 0;
	my $receiver_name = '';
	my $subject = '';
	my $body = '';
	my $check = 1;

	if ($cgi->param('cancel')) {
		$replyid = $session->param('replyid');
		$subject = $session->param('subject');
		$body = $session->param('body');
		if (!$subject) {
			$msg .= '���b�Z�[�W�̏�񂪎����܂����B';
			$check = 0;
		}
	} else {
		$replyid = $cgi->param('replyid');
		$receiver_userid = $cgi->param('receiver_userid');
		$subject = $cgi->param('subject');
		$body = $cgi->param('body');
		if (!$replyid && !$receiver_userid) {
			$msg .= '�p�����[�^���s���ł��B';
			$check = 0;
		}
	}
	if ($check) {
		# �ԐM
		if ($replyid) {
			my ($source_sender_userid, $source_subject, $source_body) = &getMessageInfo($replyid);
			if ($source_sender_userid) {
				$receiver_userid = $source_sender_userid;
				$reply_subject = $source_subject;
				$reply_body = $source_body;
				$receiver_name = &getUserName($receiver_userid);
				if (!$receiver_name) {
					$msg .= '�ԐM��̃��[�U�[�����݂��܂���B';
					$check = 0;
				}
			} else {
				$msg .= '�ԐM���郁�b�Z�[�W�����݂��܂���B';
				$check = 0;
			}
			if (!$cgi->param('submit') && !$cgi->param('cancel')) {
				if ($reply_subject =~ /^Re\:/) {
					$subject = $reply_subject;
				} else {
					$subject = 'Re: '.$reply_subject;
				}
				my @lines = split(/\n/, $reply_body);
				$body = '';
				foreach my $line(@lines) {
					$body .= '> '.$line."\n";
				}
			}
		} else {
			if ($cgi->param('cancel')) {
				$receiver_userid = $session->param('receiver_userid');
			} else {
				$receiver_userid = $cgi->param('receiver_userid');
			}
			$receiver_name = &getUserName($receiver_userid);
			if (!$receiver_name) {
				$msg .= '���M��̃��[�U�[�����݂��܂���B';
				$check = 0;
			}
		}
	}
	if ($check) {
		# �ԐMID
		if ($tmpl->query(name => 'REPLYID') eq 'VAR') {
			$tmpl->param(REPLYID => &convertOutput($replyid));
		}
		# �ԐM���T�u�W�F�N�g
		if ($tmpl->query(name => 'REPLY_SUBJECT') eq 'VAR') {
			$tmpl->param(REPLY_SUBJECT => &convertOutput($reply_subject));
		}
		# �ԐM���{��
		if ($tmpl->query(name => 'REPLY_BODY') eq 'VAR') {
			$tmpl->param(REPLY_BODY => &convertOutput($reply_body, 1));
		}

		# ����ID
		if ($tmpl->query(name => 'RECEIVER_USERID') eq 'VAR') {
			$tmpl->param(RECEIVER_USERID => &convertOutput($receiver_userid));
		}
		# ���於�O
		if ($tmpl->query(name => 'RECEIVER_NAME') eq 'VAR') {
			$tmpl->param(RECEIVER_NAME => &convertOutput($receiver_name));
		}
		# �T�u�W�F�N�g
		if ($tmpl->query(name => 'SUBJECT') eq 'VAR') {
			$tmpl->param(SUBJECT => &convertOutput($subject));
		}
		# �{��
		if ($tmpl->query(name => 'BODY') eq 'VAR') {
			$tmpl->param(BODY => &convertOutput($body));
		}

	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}


#############################
# �ԐM���̃��b�Z�[�W���擾
sub getMessageInfo($) {
	my $replyid = shift;
	my $sql = 'SELECT sender_userid, subject, body FROM messages WHERE receiver_userid=? AND messageid=?';
	my @bind = ($session->param('userid'), $replyid);
	my @message = &selectFetchArray($dbh, $sql, @bind);
	if (@message) {
		return @message;
	}
	return 0;
}

#################
# ���[�U�[���擾
sub getUserName($) {
	my $userid = shift;
	my $sql = 'SELECT name FROM users WHERE userid=? and deleteflag=?';
	my @bind = ($userid, 0);
	my $user = &selectFetch($dbh, $sql, @bind);
	if ($user) {
		return $user;
	}
	return 0;
}

###############
# ���̓`�F�b�N
sub checkMessage() {
	if ($msg) {
		return 0;
	}

	# �ԐM
	my $replyid = $cgi->param('replyid') + 0;
	if ($replyid) {
		my @bind = ($session->param('userid'), $replyid);
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE receiver_userid=? AND messageid=?', @bind);
		if (!$count) {
			$msg .= '�ԐM�悪�s���ł��B';
			return 0;
		}
	}
	
	# ����
	my $receiver_userid = $cgi->param('receiver_userid') + 0;
	my $receiver_name = '';
	if ($receiver_userid) {
		my @bind = ($receiver_userid, 0);
		$receiver_name = &selectFetch($dbh, 'SELECT name FROM users WHERE userid=? AND deleteflag=?', @bind);
		if (!$receiver_name) {
			$msg .= '���悪�s���ł��B';
			return 0;
		}
	} else {
		$msg .= '���悪�s���ł��B';
		return 0;
	}
	
	# �T�u�W�F�N�g
	my $subject = $cgi->param('subject');
	$msg .= &checkString('�T�u�W�F�N�g', $subject, 255, 1);
	if ($msg) {
		return 0;
	}

	# �{��
	my $body = $cgi->param('body');
	$msg .= &checkString('�{��', $body, 2000, 1);
	if ($msg) {
		return 0;
	}

	# �d���`�F�b�N
	my @bind = ($session->param('userid'), $receiver_userid, $subject, $body);
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE sender_userid=? AND receiver_userid=? AND subject=? AND body=? AND DATE_ADD(sendtime, INTERVAL 5 MINUTE) > now()', @bind);
	if ($count) {
		$msg .= '�������b�Z�[�W�𑱂��đ��M�ł��܂���B';
		return 0;
	}

	# ���̓`�F�b�N�����I�I
	$session->param('replyid', $replyid);
	$session->param('receiver_userid', $receiver_userid);
	$session->param('receiver_name', $receiver_name);
	$session->param('subject', $subject);
	$session->param('body', $body);
	$session->flush();
	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect('sendmessageconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# �Z�b�V������ Cookie ���ߍ���
		print $cgi->redirect('sendmessageconfirm.cgi');
	}

	return 1;
}

