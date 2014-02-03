#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use Jcode;
use HTML::Template;
use MIME::WordDecoder;
use MIME::Parser;
require './config.pl';
require './global.pl';
require './vars.pl';
require './mail.pl';
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


		# ���[�����e�m�F
		&receiveMail();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '���[�����e�m�F');

		# ��ʕ\��
		&disp;

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

################
# ���[�����e����
sub receiveMail($) {
	MIME::WordDecoder->default(
		MIME::WordDecoder->new( [
			'*' => sub { jcode(shift)->sjis },
			]
		)
	);
	my $oParse = new MIME::Parser;
	# $oParse->output_dir($config{'pop3'}); 
	$oParse->output_dir($config{'sessiondir'});

	my $oPop = Net::POP3->new($config{'pop3'}, Timeout => 60) or die "Can't not open account.";

	# ���O�C��
	$oPop->login($config{'pop3_user'}, $config{'pop3_pass'});
	
	my $rhMsg = $oPop->list();		#���b�Z�[�WID�̃n�b�V�����擾����
	
	my $mailkeyChecked = 0;
	my $successCount = 0;

	foreach my $sMsgId (keys %$rhMsg) {
		my $raCont = $oPop->get($sMsgId);
		my $oEnt = $oParse->parse_data($raCont);
		my $oHead = $oEnt->head;
		my %postData = ();

		# print "\n===============================================\n";
		# print "From:", unmime($oHead->get('From'));
		# print "To	:", unmime($oHead->get('To'));
		# print "Subj:", unmime($oHead->get('Subject'));
		$postData{'subject'} = unmime($oHead->get('Subject'));
		chomp($postData{'subject'});
		my ($mailkeyid, $keystr, $kind, $id, $registuserid) = &checkSubject($postData{'subject'});
		if ($mailkeyid) {
	 		PrnCont(\%postData, $oEnt);
	 		my $success = &registData($postData{'subject'}, $kind, $id, $registuserid, $postData{'body'}, $postData{'file1'}, $postData{'file2'}, $postData{'file3'});

			# �o�^����
			if ($success) {
				$successCount++;
				&doDB($dbh, 'UPDATE mailkeys SET deleteflag=? WHERE mailkeyid=?', ('1', $mailkeyid));
				if ($cgi->param('mailkey') eq $postData{'subject'}) {
					$mailkeyChecked = 1;
				}
			}
		}
		$oPop->delete($sMsgId);
	}

	if ($cgi->param('mailkey')) {
		if ($mailkeyChecked) {
			$msg = '���e���m�F���܂����B';
		} else {
			if ($successCount) {
				$msg = '���e���m�F�ł��܂���ł������A�V�������b�Z�[�W��'.$successCount.'������܂����B';
			} else {
				$msg .= '���e���m�F�ł��܂���ł����B';
			}
		}
	} else {
		$msg = '�m�F���I�����܂����B';
		if ($successCount) {
			$msg .= '�V�������b�Z�[�W��'.$successCount.'������܂����B';
		} else {
			$msg .= '�V�������b�Z�[�W�͂���܂���ł����B';
		}
	}

	# ���O�I�t
	$oPop->quit;
}

############################
# ���[���T�u�W�F�N�g�`�F�b�N
sub checkSubject() {
	my $subject = shift;
	if ($subject =~ /^post(\d+)_(.+)$/) {
		my $mailkeyid = $1;
		my $keystr = $2;
		my $sql = 
			'SELECT'.
			' a.kind,'.
			' a.id,'.
			' a.registuserid'.
			' FROM'.
			' mailkeys a,'.
			' users b'.
			' WHERE'.
			' a.registuserid=b.userid'.
			' AND a.mailkeyid=?'.
			' AND a.keystr=?'.
			' AND a.deleteflag=?'.
			' AND b.deleteflag=?';
		my @bind = ($mailkeyid, $keystr, '0', '0');
		my ($kind, $id, $registuserid) = &selectFetchArray($dbh, $sql, @bind);
		if ($kind) {
			return ($mailkeyid, $keystr, $kind, $id, $registuserid);
		}
	} else {
		return 0;
	}
}



################################
# ���[���̓��e���m�F
sub PrnCont($;$;$) {
	my($postData, $oEnt, $iLvl) = @_;

	$iLvl = 0 unless($iLvl);
	unless ($oEnt->is_multipart) {
		# �V���O���p�[�g
		# print "SINGLE:", jcode($oEnt->bodyhandle->as_string)->sjis;
		$$postData{'body'} = jcode($oEnt->bodyhandle->as_string)->sjis;
	} else {
		# �}���`�p�[�g
		my $nCnt = $oEnt->parts;		#Count of Parts
		for (my $i=0; $i<$nCnt;$i++) {
			if($oEnt->parts($i)->is_multipart) {
				#�}���`�p�[�g�̃l�X�g
				# print "PARTS: $i (Nested)\n";
				PrnCont($postData, $oEnt->parts($i), $iLvl+1);
			} else {
				#���ʂ̃}���`�p�[�g
				# print "--------------------------------------------------\n";
				# print "PART:", ref($oEnt), " LVL:$iLvl\n";
				# print "PATH:", $oEnt->parts($i)->bodyhandle->path, "\n";
				# print "TYPE:", $oEnt->parts($i)->mime_type, "\n";
 				if ($oEnt->parts($i)->mime_type eq "text/plain") {
					# print "TEXT:\n";
					# print jcode($oEnt->parts($i)->bodyhandle->as_string)->sjis, "\n"
					$$postData{'body'} = jcode($oEnt->parts($i)->bodyhandle->as_string)->sjis;
				} elsif($oEnt->parts($i)->mime_type eq "text/html") {
					# print "HTML:\n";
					# print jcode($oEnt->parts($i)->bodyhandle->as_string)->sjis, "\n"
				} else {
					my $sPath = $oEnt->parts($i)->bodyhandle->path();
					# print "--FILES--------------------\n";
					# print "PATH:", $sPath, "\n";
					if (&checkFileExt($sPath)) {
						# �t�@�C��1
						if (!$$postData{'file1'}) {
							$$postData{'file1'} = $sPath;
						# �t�@�C��2
						} elsif (!$$postData{'file2'}) {
							$$postData{'file2'} = $sPath;
						# �t�@�C��3
						} elsif (!$$postData{'file3'}) {
							$$postData{'file3'} = $sPath;
						}
					}
				}
			}
		}
	}
}

################################
# �t�@�C���L�����m�F
sub checkFileExt() {
	my $file = shift;
	my $ext = '';
	if ($file =~ m|(\.[^./\\]+)$|) {
		$ext = lc($1);
	}
	if ($ext ne '.jpg' && $ext ne '.jpeg' && $ext ne '.gif' && $ext ne '.png') {
		return 0;
	} else {
		return 1;
	}
}


#######
# �o�^
sub registData($) {
	my ($key, $kind, $id, $registuserid, $body, $file1, $file2, $file3) = @_;
	$body =~ s/\r\n/\n/g;
	$body =~ s/^\n+//;
	$body =~ s/\n+$//;
	my $title = '';
	if ($kind eq 'tp') {
		# �g�s�b�N�̓��̓`�F�b�N
		my @mailBody = split("\n", $body);
		chomp(@mailBody);
		$title = shift(@mailBody);
		$body = '';
		foreach (@mailBody) {
			$body .= $_."\n";
		}
		$body =~ s/^\n+//;
		$body =~ s/\n+$//;
		
		# �g�s�b�N�^�C�g��
		$msg .= &checkString('�^�C�g��', $title, 255, 1);
		if ($msg) {
			return 0;
		}
	}
	# �{��
	if (!$body) {
		$body = '(�{���Ȃ�)';
	}
	$msg .= &checkString('�{��', $body, 2000, 1);
	if ($msg) {
		return 0;
	}

	# �ʐ^1
	my $fname1 = '';
	my $lname1 = '';
	my $sname1 = '';
	if ($file1) {
		my ($lname, $sname) = &attachFile($file1, 1, $key);
		if (!$lname) {
			$msg .= '�ʐ^1�̎�ʂ��s���ł��B';
			return 0;
		} else {
			$lname1 = $lname;
			$sname1 = $sname;
		}
	}

	# �ʐ^2
	my $fname2 = '';
	my $lname2 = '';
	my $sname2 = '';
	if ($file2) {
		my ($lname, $sname) = &attachFile($file2, 2, $key);
		if (!$lname) {
			$msg .= '�ʐ^2�̎�ʂ��s���ł��B';
			return 0;
		} else {
			$lname2 = $lname;
			$sname2 = $sname;
		}
	}

	# �ʐ^3
	my $fname3 = '';
	my $lname3 = '';
	my $sname3 = '';
	if ($file3) {
		my ($lname, $sname) = &attachFile($file3, 3, $key);
		if (!$lname) {
			$msg .= '�ʐ^3�̎�ʂ��s���ł��B';
			return 0;
		} else {
			$lname3 = $lname;
			$sname3 = $sname;
		}
	}

	# �g�s�b�N�o�^
	if ($kind eq 'tp') {
		my %data;
		$data{'title'} = $title;
		$data{'body'} = $body;
		$data{'fname1'} = $fname1;
		$data{'lname1'} = $lname1;
		$data{'sname1'} = $sname1;
		$data{'fname2'} = $fname2;
		$data{'lname2'} = $lname2;
		$data{'sname2'} = $sname2;
		$data{'fname3'} = $fname3;
		$data{'lname3'} = $lname3;
		$data{'sname3'} = $sname3;
		$msg .= &submitTopic($dbh, $id, \%data, $registuserid);
		if ($msg) {
			return 0;
		}
	# �g�s�b�N�R�����g�o�^
	} elsif ($kind eq 'tc') {
		my %data;
		$data{'body'} = $body;
		$data{'fname1'} = $fname1;
		$data{'lname1'} = $lname1;
		$data{'sname1'} = $sname1;
		$data{'fname2'} = $fname2;
		$data{'lname2'} = $lname2;
		$data{'sname2'} = $sname2;
		$data{'fname3'} = $fname3;
		$data{'lname3'} = $lname3;
		$data{'sname3'} = $sname3;
		$msg .= &submitTopicComment($dbh, $id, \%data, $registuserid);
		if ($msg) {
			return 0;
		}
	}

	return 1;
}


