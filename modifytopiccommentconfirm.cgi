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
my $forumid = 0;
my $forumname = '';
my $forumnote = '';
my $topicid = 0;
my $topictitle = '';
my $topicbody = '';
my $topiccommentid = 0;
my $oldtopiccommentbody = '';

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
			if (&isMobile()) {
				# �Z�b�V������ URL ���ߍ���
				print $cgi->redirect("modifytopiccomment.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("modifytopiccomment.cgi?cancel=1");
			}
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �g�s�b�N�R�����g���擾
			&getTopicCommentInfo();

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &modifyTopicComment();
			}

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N�R�����g�C���m�F');

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

	if (!$msg) {
		my $body = $session->param('body');
		my $fname1 = $session->param('fname1');
		my $deletefile1 = $session->param('deletefile1');
		my $fname2 = $session->param('fname2');
		my $deletefile2 = $session->param('deletefile2');
		my $fname3 = $session->param('fname3');
		my $deletefile3 = $session->param('deletefile3');

		if ($forumname) {
			# �t�H�[����ID
			if ($forumname && $tmpl->query(name => ['FORUMID']) eq 'VAR') {
				$tmpl->param(FORUMID => &convertOutput($forumid));
			}
			# �t�H�[����URL
			if ($tmpl->query(name => ['FORUMURL']) eq 'VAR') {
				my $url = 'forum.cgi?forumid='.$forumid;
				if (&isMobile) {
						$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(FORUMURL => &convertOutput($url));
			}
			# �t�H�[������
			if ($forumname && $tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
				$tmpl->param(FORUMNAME => &convertOutput($forumname));
			}
			# �t�H�[��������
			if ($forumnote && $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
				$tmpl->param(FORUMNOTE => &convertOutput($forumnote, 1));
			}
			# �g�s�b�NID
			if ($tmpl->query(name => ['TOPICID']) eq 'VAR') {
				$tmpl->param(TOPICID => $topicid);
			}
			# �g�s�b�NURL
			if ($tmpl->query(name => ['TOPICURL']) eq 'VAR') {
				my $url = 'topic.cgi?topicid='.$topicid;
				if (&isMobile) {
						$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(TOPICURL => &convertOutput($url));
			}
			# �g�s�b�N�^�C�g��
			if ($tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
				$tmpl->param(TOPICTITLE => &convertOutput($topictitle));
			}
			# �g�s�b�N�{��
			if ($tmpl->query(name => ['TOPICBODY']) eq 'VAR') {
				$tmpl->param(TOPICBODY => &convertOutput($topicbody, 1));
			}
			# �g�s�b�N�R�����gID
			if ($tmpl->query(name => ['TOPICCOMMENTID']) eq 'VAR') {
				$tmpl->param(TOPICCOMMENTID => &convertOutput($topiccommentid, 1));
			}
			# �Â��g�s�b�N�R�����g
			if ($tmpl->query(name => ['OLDTOPICCOMMENTBODY']) eq 'VAR') {
				$tmpl->param(OLDTOPICCOMMENTBODY => &convertOutput($oldtopiccommentbody, 1));
			}
			# �R�����g
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body, 1));
			}

			# �Y�t�t�@�C��1
			if ($tmpl->query(name => ['FILE1LARGEURL']) eq 'VAR') {
				my $lname1 = &getPublishFile('tc'.$topiccommentid.'_1');
				if ($lname1) {
					$tmpl->param(FILE1LARGEURL => $lname1);
					if ($tmpl->query(name => ['FILE1SMALLURL']) eq 'VAR') {
						my $sname1 = &getPublishFile('tc'.$topiccommentid.'_1_s');
						if ($sname1) {
							$tmpl->param(FILE1SMALLURL => $sname1);
						}
					}
					if ($deletefile1 && $tmpl->query(name => ['DELETEFILE1CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE1CHECKED => 'checked');
					}
				}
			}

			# �Y�t�t�@�C��2
			if ($tmpl->query(name => ['FILE2LARGEURL']) eq 'VAR') {
				my $lname2 = &getPublishFile('tc'.$topiccommentid.'_2');
				if ($lname2) {
					$tmpl->param(FILE2LARGEURL => $lname2);
					if ($tmpl->query(name => ['FILE2SMALLURL']) eq 'VAR') {
						my $sname2 = &getPublishFile('tc'.$topiccommentid.'_2_s');
						if ($sname2) {
							$tmpl->param(FILE2SMALLURL => $sname2);
						}
					}
					if ($deletefile2 && $tmpl->query(name => ['DELETEFILE2CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE2CHECKED => 'checked');
					}
				}
			}

			# �Y�t�t�@�C��3
			if ($tmpl->query(name => ['FILE3LARGEURL']) eq 'VAR') {
				my $lname3 = &getPublishFile('tc'.$topiccommentid.'_3');
				if ($lname3) {
					$tmpl->param(FILE3LARGEURL => $lname3);
					if ($tmpl->query(name => ['FILE3SMALLURL']) eq 'VAR') {
						my $sname3 = &getPublishFile('tc'.$topiccommentid.'_3_s');
						if ($sname3) {
							$tmpl->param(FILE3SMALLURL => $sname3);
						}
					}
					if ($deletefile3 && $tmpl->query(name => ['DELETEFILE3CHECKED']) eq 'VAR') {
						$tmpl->param(DELETEFILE3CHECKED => 'checked');
					}
				}
			}

			# �ʐ^1
			if ($tmpl->query(name => 'FILE1') eq 'VAR') {
				$tmpl->param(FILE1 => &convertOutput($fname1));
			}
			# �ʐ^2
			if ($tmpl->query(name => 'FILE2') eq 'VAR') {
				$tmpl->param(FILE2 => &convertOutput($fname2));
			}
			# �ʐ^3
			if ($tmpl->query(name => 'FILE3') eq 'VAR') {
				$tmpl->param(FILE3 => &convertOutput($fname3));
			}

		} else {
			$msg .= '�R�����g�̏�񂪎����܂����B';
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => &convertOutput($msg));
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

##########################
# �g�s�b�N�R�����g���擾
sub getTopicCommentInfo() {
	# �g�s�b�NID
	$topiccommentid = $session->param('topiccommentid');

	my $sql = 
		'SELECT a.forumid, a.name, a.note, b.topicid, b.title, b.body, c.body'.
		' FROM forums a, topics b, topiccomments c'.
		' WHERE a.forumid=b.forumid AND b.topicid=c.topicid AND c.topiccommentid=? AND a.deleteflag=? AND b.deleteflag=? AND c.deleteflag=? AND a.powerlevel<=?';
	my @bind = ($topiccommentid, '0', '0', '0', $session->param('powerlevel'));
	# �Ǘ��҈ȊO�͏������񂾓��l�̂�
	if ($session->param('powerlevel') < 5) {
		$sql .= ' AND c.registuserid=?';
		push(@bind, $session->param('userid'));
	}
	my ($fid, $fname, $fnote, $tid, $ttitle, $tbody, $cbody) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topicid = $tid;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	$oldtopiccommentbody = $cbody;
	if (!$oldtopiccommentbody) {
		$msg .= '�p�����[�^���s���ł��B';
	}
}

###############
# �g�s�b�N�C��
sub modifyTopicComment() {
	if ($msg) {
		return 0;
	}

	my $body = $session->param('body');
	my $deletefile1 = $session->param('deletefile1');
	my $fname1 = $session->param('fname1');
	my $lname1 = $session->param('lname1');
	my $sname1 = $session->param('sname1');
	my $deletefile2 = $session->param('deletefile2');
	my $fname2 = $session->param('fname2');
	my $lname2 = $session->param('lname2');
	my $sname2 = $session->param('sname2');
	my $deletefile3 = $session->param('deletefile3');
	my $fname3 = $session->param('fname3');
	my $lname3 = $session->param('lname3');
	my $sname3 = $session->param('sname3');

	# �Ǘ��҈ȊO�͏������񂾓��l�̂�
	if ($session->param('powerlevel') < 5) {
		my @bind = ($topiccommentid, $session->param('userid'), '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE topiccommentid=? AND registuserid=? AND deleteflag=?', @bind);
		if (!$count) {
			$msg .= '�p�����[�^���s���ł��B';
			return 0;
		}
	}

	# DB �o�^
	my @bind = ($body, $topiccommentid);
	my $sql = 
		'UPDATE topiccomments SET '.
		'body=? '.
		'where topiccommentid=?';
	&doDB($dbh, $sql, @bind);

	# ���t�@�C�����폜
	if ($lname1 || $deletefile1) {
		&deleteFile('tc'.$topiccommentid.'_1');
	}
	if ($lname2 || $deletefile2) {
		&deleteFile('tc'.$topiccommentid.'_2');
	}
	if ($lname3 || $deletefile3) {
		&deleteFile('tc'.$topiccommentid.'_3');
	}
	
	if (&publishFile($lname1, 'tc'.$topiccommentid.'_1')) {
		&publishFile($sname1, 'tc'.$topiccommentid.'_1_s');
	}
	if (&publishFile($lname2, 'tc'.$topiccommentid.'_2')) {
		&publishFile($sname2, 'tc'.$topiccommentid.'_2_s');
	}
	if (&publishFile($lname3, 'tc'.$topiccommentid.'_3')) {
		&publishFile($sname3, 'tc'.$topiccommentid.'_3_s');
	}

	$msg .= '�R�����g���C�����܂����B';
	$session->clear(['topiccommentid', 'body']);
	$session->param('msg', $msg);
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("topic.cgi?topiccommentid=$topiccommentid&$config{'sessionname'}=$sid#$topiccommentid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('topic.cgi?topiccommentid='.$topiccommentid.'#'.$topiccommentid);
	}

	return 1;
}

