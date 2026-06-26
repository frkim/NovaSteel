# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY libs/NovaSteel.Contracts/NovaSteel.Contracts.csproj libs/NovaSteel.Contracts/
COPY apps/steel_factory_simulator/src/SteelFactorySimulator/SteelFactorySimulator.csproj apps/steel_factory_simulator/src/SteelFactorySimulator/
RUN dotnet restore apps/steel_factory_simulator/src/SteelFactorySimulator/SteelFactorySimulator.csproj
COPY libs/NovaSteel.Contracts/ libs/NovaSteel.Contracts/
COPY apps/steel_factory_simulator/src/SteelFactorySimulator/ apps/steel_factory_simulator/src/SteelFactorySimulator/
RUN dotnet publish apps/steel_factory_simulator/src/SteelFactorySimulator/SteelFactorySimulator.csproj -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
ENV ASPNETCORE_URLS=http://+:80 \
    Simulator__Transport=InMemory
EXPOSE 80
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "SteelFactorySimulator.dll"]
