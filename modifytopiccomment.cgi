#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './post.pl';
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

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �g�s�b�N�R�����g���擾
		&getTopicCommentInfo();

		# �o�^
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &checkTopicComment();
		}

		# ��ʕ\��
		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N�R�����g�C��');

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

	# �g�s�b�N�R�����g���L��
	if ($oldtopiccommentbody) {
		# �t�H�[����ID
		if ($tmpl->query(name => ['FORUMID']) eq 'VAR') {
			$tmpl->param(FORUMID => $forumid);
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
		if ($tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($forumname));
		}
		# �t�H�[��������
		if ($tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
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
			$tmpl->param(TOPICCOMMENTID => &convertOutput($topiccommentid));
		}
		# �Â��g�s�b�N�R�����g
		if ($tmpl->query(name => ['OLDTOPICCOMMENTBODY']) eq 'VAR') {
			$tmpl->param(OLDTOPICCOMMENTBODY => &convertOutput($oldtopiccommentbody, 1));
		}

		my $body = '';
		my $deletefile1 = '';
		my $deletefile2 = '';
		my $deletefile3 = '';
		my $check = 1;
		if ($cgi->param('cancel')) {
			$body = $session->param('body');
			$deletefile1 = $session->param('deletefile1');
			$deletefile2 = $session->param('deletefile2');
			$deletefile3 = $session->param('deletefile3');
			if (!$body) {
				$msg .= '�R�����g�̏�񂪎����܂����B';
				$check = 0;
			}
		} elsif ($cgi->param('submit')) {
			$body = $cgi->param('body');
			$deletefile1 = $cgi->param('deletefile1');
			$deletefile2 = $cgi->param('deletefile2');
			$deletefile3 = $cgi->param('deletefile3');
		} else {
			$body = $oldtopiccommentbody;
		}

		if ($check) {
			# �{��
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body));
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
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

##########################
# �g�s�b�N�R�����g���擾
sub getTopicCommentInfo() {
	# �g�s�b�N�R�����gID
	if ($cgi->param('cancel')) {
		$topiccommentid = $session->param('topiccommentid');
	} else {
		$topiccommentid = $cgi->param('topiccommentid');
	}
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
# ���̓`�F�b�N
sub checkTopicComment() {
	if ($msg) {
		return 0;
	}

	my %data;
	$data{'body'} = $cgi->param('body');
	$data{'file1'} = $cgi->param('file1');
	$data{'file2'} = $cgi->param('file2');
	$data{'file3'} = $cgi->param('file3');
	$msg .= &postData($dbh, $topicid, 'tc', \%data, $sid);
	if ($msg) {
		return 0;
	}
	my $deletefile1 = $cgi->param('deletefile1');
	my $deletefile2 = $cgi->param('deletefile2');
	my $deletefile3 = $cgi->param('deletefile3');

	# ���̓`�F�b�N�����I�I
	$session->param('topiccommentid', $topiccommentid);
	$session->param('body', $data{'body'});
	$session->param('fname1', $data{'fname1'});
	$session->param('lname1', $data{'lname1'});
	$session->param('sname1', $data{'sname1'});
	$session->param('fname2', $data{'fname2'});
	$session->param('lname2', $data{'lname2'});
	$session->param('sname2', $data{'sname2'});
	$session->param('fname3', $data{'fname3'});
	$session->param('lname3', $data{'lname3'});
	$session->param('sname3', $data{'sname3'});
	$session->param('deletefile1', $deletefile1);
	$session->param('deletefile2', $deletefile2);
	$session->param('deletefile3', $deletefile3);
	$session->flush();
	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect('modifytopiccommentconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# �Z�b�V������ Cookie ���ߍ���
		print $cgi->redirect('modifytopiccommentconfirm.cgi');
	}

	return 1;
}

