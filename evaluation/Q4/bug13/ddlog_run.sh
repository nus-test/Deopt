export DDLOG_HOME=/tmp/differential-datalog
/root/.local/bin/ddlog -i $1.dl
cd $1_ddlog && cargo build --release
./target/release/$1_cli