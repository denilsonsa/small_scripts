#!/bin/bash
# vi:et:sw=4

# Quick, simple-to-use, menu/wizard-based text interface to help debugging
# network issues. I wrote this so my mother could run it and tell me the output
# over the phone.

ESC_DEFAULT=$'\x1b[0m'
ESC_BOLD=$'\x1b[1m'
ESC_GRAY=$'\x1b[1;30m'
ESC_RED=$'\x1b[1;31m'
ESC_GREEN=$'\x1b[1;32m'
ESC_YELLOW=$'\x1b[1;33m'
ESC_BLUE=$'\x1b[1;34m'
ESC_MAGENTA=$'\x1b[1;35m'
ESC_CYAN=$'\x1b[1;36m'
ESC_WHITE=$'\x1b[1;37m'

PS3="${ESC_CYAN}Digite o número da opção desejada:${ESC_DEFAULT} "

SERVICES=(
    'apache2'
    'bluetooth'
    'cupsd'
    'dhcpd'
    'hostapd'
    'named'
    'net.eth0'
    'net.eth1'
    'net.ppp0'
    'net.wlan0'
    'ntp-client'
    'ntpd'
    'squid'
    'sshd'
)

function echo_run() {
	echo -E "$@"
	"$@"
}


function highlight_ip_addr() {
	sed -e '
	    s/^\([0-9]\+: \)\([^ ]\+\):/\1'"${ESC_YELLOW}"'\2'"${ESC_DEFAULT}"':/ ;
		s/\(inet6\? [^ ]\+\)/'"${ESC_GREEN}"'\1'"${ESC_DEFAULT}"'/'
}

function highlight_traceroute() {
	sed -e '
        s/^\(traceroute\)\( to \)\([^,]\+\)/'"${ESC_YELLOW}"'\1'"${ESC_DEFAULT}"'\2'"${ESC_GREEN}"'\3'"${ESC_DEFAULT}"'/g ;
	    s/\([0-9.]\+ ms\)/'"${ESC_GRAY}"'\1'"${ESC_DEFAULT}"'/g ;
	    s/\*/'"${ESC_RED}"'*'"${ESC_DEFAULT}"'/g'
}

function highlight_ping() {
	sed -e '
        s/^\(PING\) \([^ ]\+ ([^)]\+)\)/'"${ESC_YELLOW}"'\1'"${ESC_DEFAULT}"' '"${ESC_GREEN}"'\2'"${ESC_DEFAULT}"'/g ;
	    s/\([0-9.]\+ packets transmitted\)/'"${ESC_CYAN}"'\1'"${ESC_DEFAULT}"'/g ;
	    s/\([0-9.]\+ received\)/'"${ESC_GREEN}"'\1'"${ESC_DEFAULT}"'/g ;
	    s/\([0-9.]\+% packet loss\)/'"${ESC_RED}"'\1'"${ESC_DEFAULT}"'/g'
}


function show_ip() {
    echo_run /sbin/ip addr show "$@" | highlight_ip_addr
}

function run_ping() {
    echo_run /bin/ping -c 10 "$@" | highlight_ping
}

function run_traceroute() {
    echo_run /usr/bin/traceroute "$@" | highlight_traceroute
}

function all_service_status() {
    for S in "${SERVICES[@]}" ; do
        PAD=`echo "${S}                 " | sed 's/^\(.\{16\}\).*$/\1/'`
        echo -n "$PAD"
        /etc/init.d/"${S}" status
    done
}


function wizard_show_ip() {
    echo
    select CHOICE in \
        'Exibir o IP da interface ppp0' \
        'Exibir todas as interfaces' \
        'Voltar' ; do
        if [ -n "$CHOICE" ] ; then
            case "$REPLY" in
                1)  show_ip ppp0
                    break
                    ;;
                2)  show_ip
                    break
                    ;;
                3)  return
                    ;;
            esac
        fi
    done
}

function wizard_ping() {
    HOST=''
    echo
    select CHOICE in \
        'Pingar 8.8.8.8' \
        'Pingar registro.br' \
        'Pingar outro host' \
        'Voltar' ; do
        if [ -n "$CHOICE" ] ; then
            case "$REPLY" in
                1)  HOST='8.8.8.8'
                    break
                    ;;
                2)  HOST='registro.br'
                    break
                    ;;
                3)  read -p 'Pingar qual host? ' HOST
                    break
                    ;;
                4)  return
                    ;;
            esac
        fi
    done
    run_ping "$HOST"
}

function wizard_traceroute() {
    HOST=''
    echo
    select CHOICE in \
        'Traçar rota para 8.8.8.8' \
        'Traçar rota para registro.br' \
        'Traçar rota para outro host' \
        'Voltar' ; do
        if [ -n "$CHOICE" ] ; then
            case "$REPLY" in
                1)  HOST='8.8.8.8'
                    break
                    ;;
                2)  HOST='registro.br'
                    break
                    ;;
                3)  read -p 'Pingar qual host? ' HOST
                    break
                    ;;
                4)  return
                    ;;
            esac
        fi
    done
    RESOLVE=''
    select CHOICE in \
        'Resolver nomes DNS (mais lento)' \
        'Não resolver nomes DNS (mais rápido)' ; do
        if [ -n "$CHOICE" ] ; then
            case "$REPLY" in
                1)  RESOLVE=''
                    break
                    ;;
                2)  RESOLVE='-n'
                    break
                    ;;
            esac
        fi
    done
    run_traceroute $RESOLVE "$HOST"
}

function wizard_services() {
    all_service_status

    ACTION=''
    echo
    select CHOICE in \
        'start' \
        'restart' \
        'stop' \
        'Voltar' ; do
        if [ -n "$CHOICE" ] ; then
            case "$REPLY" in
                1|2|3)  ACTION="${CHOICE}"
                    break
                    ;;
                4)  return
                    ;;
            esac
        fi
    done

    echo "Executar '${ACTION}' em qual serviço?"
    S=''
    select CHOICE in \
        "${SERVICES[@]}" \
        'Voltar' ; do
        if [ -n "$CHOICE" ] ; then
            case "$CHOICE" in
                Voltar) return
                    ;;
                *)  S="${CHOICE}"
                    break
                    ;;
            esac
        fi
    done

    echo_run sudo /etc/init.d/"${S}" "$ACTION"
}

function main_menu() {
    while true ; do
        echo
        select CHOICE in \
            'Mostrar endereço IP' \
            'Ping' \
            'Traçar rota' \
            'Serviços do sistema' \
            'Sair' ; do
            if [ -n "$CHOICE" ] ; then
                case "$REPLY" in
                    1)  wizard_show_ip
                        break
                        ;;
                    2)  wizard_ping
                        break
                        ;;
                    3)  wizard_traceroute
                        break
                        ;;
                    4)  wizard_services
                        break
                        ;;
                    5)  return
                        ;;
                esac
            fi
        done
    done
}

main_menu
