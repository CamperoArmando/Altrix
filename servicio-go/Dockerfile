FROM golang:1.22-alpine AS build
WORKDIR /app
COPY go.mod ./
COPY main.go ./
RUN go build -o servicio-alertas .

FROM alpine:3.20
WORKDIR /app
COPY --from=build /app/servicio-alertas .
EXPOSE 5001
CMD ["./servicio-alertas"]
