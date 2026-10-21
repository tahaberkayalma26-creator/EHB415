#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"

#include <iostream>

using namespace ns3;

void SunucuAldi(Ptr<const Packet> paket, const Address& kimden)
{
    std::cout << "t = " << Simulator::Now().GetMicroSeconds() / 1000.0 << " ms : SUNUCU paketi aldi ("
              << paket->GetSize() << " bayt)" << std::endl;
}

void IstemciAldi(Ptr<const Packet> paket)
{
    std::cout << "t = " << Simulator::Now().GetMicroSeconds() / 1000.0 << " ms : ISTEMCI cevabi aldi ("
              << paket->GetSize() << " bayt)" << std::endl;
}

int main(int argc, char* argv[])
{
    Time::SetResolution(Time::NS);

    NodeContainer dugumler;
    dugumler.Create(2);

    PointToPointHelper kablo;
    kablo.SetDeviceAttribute("DataRate", StringValue("5Mbps"));
    kablo.SetChannelAttribute("Delay", StringValue("2ms"));
    NetDeviceContainer cihazlar = kablo.Install(dugumler);

    InternetStackHelper yigin;
    yigin.Install(dugumler);
    Ipv4AddressHelper adres;
    adres.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer arayuzler = adres.Assign(cihazlar);

    UdpEchoServerHelper sunucu(9);
    ApplicationContainer sA = sunucu.Install(dugumler.Get(1));
    sA.Start(Seconds(1.0));
    sA.Stop(Seconds(10.0));

    UdpEchoClientHelper istemci(arayuzler.GetAddress(1), 9);
    istemci.SetAttribute("MaxPackets", UintegerValue(1));
    istemci.SetAttribute("Interval", TimeValue(Seconds(1.0)));
    istemci.SetAttribute("PacketSize", UintegerValue(1024));
    ApplicationContainer iA = istemci.Install(dugumler.Get(0));
    iA.Start(Seconds(2.0));
    iA.Stop(Seconds(10.0));

    sA.Get(0)->TraceConnectWithoutContext("Rx", MakeCallback(&SunucuAldi));
    iA.Get(0)->TraceConnectWithoutContext("Rx", MakeCallback(&IstemciAldi));

    std::cout << "istemci t = 2000 ms de paketi gonderecek" << std::endl;
    Simulator::Run();
    Simulator::Destroy();
    return 0;
}
