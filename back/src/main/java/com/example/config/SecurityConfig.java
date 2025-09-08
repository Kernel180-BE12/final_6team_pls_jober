package com.example.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.security.oauth2.server.resource.authentication.JwtGrantedAuthoritiesConverter;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import javax.crypto.spec.SecretKeySpec;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Value("${jwt.secret}")
    private String jwtSecret;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(authz -> authz
                        .requestMatchers("/", "/health", "/api/auth/**").permitAll()
                        .anyRequest().authenticated()
                );
        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    // AuthenticationManager 등록
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    // PasswordEncoder 등록 (비밀번호 암호화/검증에 필요)
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }


    // JWT 시크릿 키를 사용한 대칭키 디코더
    @Bean
    public JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder.withSecretKey(
            new SecretKeySpec(jwtSecret.getBytes(), "HmacSHA256")
        ).build();
    }

    // principal을 항상 accountId(Long) 으로 표준화하기 위함
    @Bean
    public Converter<Jwt, AbstractAuthenticationToken> jwtAuthConverter() {
        return new Converter<Jwt, AbstractAuthenticationToken>() {
            @Override
            public AbstractAuthenticationToken convert(Jwt jwt) {
                // 1) JWT claim에서 account_id 우선 추출, 없으면 sub 사용
                final Long accountId = firstNonNull(
                        toLong(jwt.getClaim("account_id")),
                        toLong(jwt.getClaim("sub"))
                );

                // accountId 가 없으면 인증 실패 처리
                if (accountId == null) throw new IllegalStateException("Missing account_id");

                // 2) 권한(roles/authorities) 추출
                var authorities = new JwtGrantedAuthoritiesConverter().convert(jwt);

                // 3) Authentication 객체 생성
                // - principal: accountId(Long) ← 여기서 표준화
                // - credentials: null (사용 안 함)
                // - authorities: 위에서 추출한 권한 목록
                return new JwtAuthenticationToken(jwt, authorities, String.valueOf(accountId)) {
                    @Override
                    public Object getPrincipal() {
                        // principal은 항상 Long accountId 반환
                        return accountId;
                    }
                };
            }
        };
    }

    /**
     * 두 값 중 null이 아닌 첫 번째를 반환
     * (account_id 없으면 sub 대체)
     */
    private static Long firstNonNull(Long a, Long b) {
        return a != null ? a : b;
    }

    /**
     * Object를 Long으로 안전 변환
     * - Number → longValue()
     * - String → Long.parseLong()
     * - 실패/변환 불가 → null
     */
    private static Long toLong(Object v) {
        if (v instanceof Number n) return n.longValue();
        if (v instanceof String s) {
            try {
                return Long.parseLong(s);
            } catch (NumberFormatException ignore) {
                // 숫자 변환 실패시 null 반환
            }
        }
        return null;
    }
}
