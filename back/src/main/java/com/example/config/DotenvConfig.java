package com.example.config;

import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.File;

@Configuration
public class DotenvConfig {

    @Bean
    public Dotenv dotenv() {
        // root 폴더(프로젝트 루트)의 .env 파일을 참조
        String rootPath = new File(System.getProperty("user.dir")).getParent();
        if (rootPath == null) {
            rootPath = System.getProperty("user.dir");
        }
        
        return Dotenv.configure()
                .directory(rootPath)
                .filename(".env")
                .ignoreIfMissing()
                .systemProperties()
                .load();
    }
}
