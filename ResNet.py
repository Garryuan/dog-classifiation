import torch
from torch import nn

class Bottleneck(nn.Module):

    expansion = 4

    # initialization
    def __init__(self, in_channel, out_channel, stride=1, downsample=None):
        #
        super(Bottleneck, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=out_channel,
                               kernel_size=1, stride=1, padding=0, bias=False)

        # BN Layer
        self.bn1 = nn.BatchNorm2d(out_channel)

        # relu layer
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel,
                               kernel_size=3, stride=stride, padding=1, bias=False)

        # BN layer
        self.bn2 = nn.BatchNorm2d(out_channel)

        self.conv3 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel * self.expansion,
                               kernel_size=1, stride=1, padding=0, bias=False)

        # BN layer
        self.bn3 = nn.BatchNorm2d(out_channel * self.expansion)

        self.downsample = downsample

    def forward(self, x):

        identity = x

        if self.downsample is not None:

            identity = self.downsample(x)

        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)

        x = self.conv3(x)
        x = self.bn3(x)


        x = x + identity

        x = self.relu(x)

        return x



class ResNet(nn.Module):
    # Initialization
    def __init__(self, block, blocks_num, num_classes=1000, include_top=True):

        super(ResNet, self).__init__()


        self.include_top = include_top
        self.in_channel = 64


        self.conv1 = nn.Conv2d(in_channels=3, out_channels=self.in_channel,
                               kernel_size=7, stride=2, padding=3, bias=False)


        self.bn1 = nn.BatchNorm2d(self.in_channel)


        self.relu = nn.ReLU(inplace=True)


        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)


        self.layer1 = self._make_layer(block, 64, blocks_num[0])

        self.layer2 = self._make_layer(block, 128, blocks_num[1], stride=2)
        self.layer3 = self._make_layer(block, 256, blocks_num[2], stride=2)
        self.layer4 = self._make_layer(block, 512, blocks_num[3], stride=2)


        if self.include_top:

            self.avgpool = nn.AdaptiveAvgPool2d((1, 1))  # output

            self.fc = nn.Linear(512 * block.expansion, num_classes)


        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out')



    def _make_layer(self, block, channel, block_num, stride=1):


        downsample = None


        if stride != 1 or self.in_channel != channel * block.expansion:

            downsample = nn.Sequential(

                nn.Conv2d(in_channels=self.in_channel, out_channels=channel * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(channel * block.expansion))


        layers = []

        layers.append(block(self.in_channel, channel, stride=stride, downsample=downsample))

        self.in_channel = channel * block.expansion


        for _ in range(1, block_num):
            layers.append(block(self.in_channel, channel))

        return nn.Sequential(*layers)

    def forward(self, x):

        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)


        if self.include_top:
            # Average pool
            x = self.avgpool(x)
            # convert to vector
            x = torch.flatten(x, 1)

            x = self.fc(x)

        return x

def resnet50(num_classes=1000, include_top=True):
    return  ResNet(Bottleneck, [3,4,6,3], num_classes=num_classes, include_top=include_top)