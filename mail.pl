use strict;
use Net::SMTP;
use MIME::Entity;
use MIME::Words qw (:all);
use Net::POP3;
use MIME::Parser;
require './jcode.pl';
require './config.pl';

# 設定読込
my %config = &config;

#################
# JIS コード変換
sub convJis($) {
	my $sWk = shift;
	&jcode::convert(\$sWk, 'jis');
	return $sWk;
}

#############
# メール送信
sub sendMail($) {
	my ($from, $to, $sub, $body, $fromName, $toName) = @_;

	if ($config{'popbeforesmtp'}) {
		# POP3 before SMTP
		my $oPop = Net::POP3->new($config{'pop3'}, Timeout => 60) or die "Can't not open account.";
		$oPop->login($config{'pop3_user'}, $config{'pop3_pass'});
		$oPop->quit;
	}
	
	my $smtp = Net::SMTP->new($config{'smtp'}) or die;

	$smtp->mail($from);
	$smtp->to($to);
	$smtp->data();
	my $mimeFrom;
	if ($fromName) {
		$mimeFrom = &encode_mimeword(&convJis($fromName), 'B', 'iso-2022-jp') .'<'.$from.'>';
	} else {
		$mimeFrom = $from;
	}
	my $mimeTo;
	if ($toName) {
		$mimeTo = &encode_mimeword(&convJis($toName), 'B', 'iso-2022-jp') .'<'.$to.'>';
	} else {
		$mimeTo = $to;
	}
	my $mimeSub = &encode_mimeword(&convJis($sub), 'B', 'iso-2022-jp');
	my $jisBody = &convJis($body);
	my $mime = MIME::Entity->build(
		To => $mimeTo, 
		From => $mimeFrom,
		Subject => $mimeSub,
		Type => 'text/plain;charset="iso-2022-jp"',
		Data => $jisBody,
		Encoding => "7bit"
	);
	$smtp->datasend($mime->stringify);
	$smtp->dataend();
	$smtp->quit();
}

1;
